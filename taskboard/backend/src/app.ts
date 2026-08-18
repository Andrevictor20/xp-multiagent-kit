import Fastify from 'fastify';
import { z } from 'zod';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import pg from 'pg';
import fastifyJwt from '@fastify/jwt';
import fastifyRateLimit from '@fastify/rate-limit';
import bcrypt from 'bcrypt';
import dotenv from 'dotenv';
dotenv.config();

const userSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
  name: z.string().optional()
});

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string()
});

export const buildServer = async () => {
  const app = Fastify({ logger: true });
  
  await app.register(fastifyRateLimit, {
    max: 50,
    timeWindow: '1 minute',
    global: true,
    allowList: []
  });

  if (!process.env.JWT_SECRET) {
    throw new Error('FATAL: JWT_SECRET environment variable is missing. Refusing to start.');
  }

  await app.register(fastifyJwt, {
    secret: process.env.JWT_SECRET
  });

  const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
  const adapter = new PrismaPg(pool);
  const prisma = new PrismaClient({ adapter });

  app.get('/health', async () => {
    return { status: 'ok' };
  });

  app.get('/stats', async () => {
    const users = await prisma.user.count();
    const projects = await prisma.project.count();
    return { users, projects };
  });

  app.post('/login', {
    config: {
      rateLimit: {
        max: 3,
        timeWindow: '1 minute'
      }
    }
  }, async (request, reply) => {
    const parsed = loginSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({ error: 'Invalid input' });
    }

    const { email, password } = parsed.data;
    const user = await prisma.user.findUnique({ where: { email } });

    if (!user) {
      return reply.status(401).send({ error: 'Invalid credentials' });
    }

    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) {
      return reply.status(401).send({ error: 'Invalid credentials' });
    }

    const token = app.jwt.sign({ id: user.id, email: user.email });
    return reply.send({ token });
  });

  app.post('/users', async (request, reply) => {
    const parsed = userSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({ error: 'Invalid input' });
    }

    const { email, password, name } = parsed.data;
    const hashedPassword = await bcrypt.hash(password, 10);

    try {
      const user = await prisma.user.create({
        data: {
          email,
          password: hashedPassword,
          name
        }
      });

      const { password: _, ...userWithoutPassword } = user;
      return reply.status(201).send(userWithoutPassword);
    } catch (e: any) {
      if (e.code === 'P2002') {
        return reply.status(409).send({ error: 'Email already exists' });
      }
      return reply.status(500).send({ error: 'Internal Server Error' });
    }
  });
  
  const projectSchema = z.object({
    name: z.string().min(1),
    description: z.string().optional(),
    ownerId: z.string().uuid()
  });

  app.post('/projects', async (request, reply) => {
    const parsed = projectSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({ error: 'Invalid input' });
    }

    const { name, description, ownerId } = parsed.data;

    try {
      const project = await prisma.project.create({
        data: { name, description, ownerId }
      });
      return reply.status(201).send(project);
    } catch (e: any) {
      request.log.error(e);
      return reply.status(500).send({ error: 'Internal Server Error', details: e.message });
    }
  });

  app.decorate('authenticate', async function (request: any, reply: any) {
    try {
      await request.jwtVerify();
    } catch (err) {
      reply.send(err);
    }
  });

  app.get('/projects/:id', {
    preValidation: [app.authenticate as any]
  }, async (request: any, reply: any) => {
    const { id } = request.params;
    const userId = request.user.id;

    const project = await prisma.project.findUnique({
      where: { id }
    });

    if (!project) {
      return reply.status(404).send({ error: 'Project not found' });
    }

    if (project.ownerId !== userId) {
      return reply.status(403).send({ error: 'Forbidden' });
    }

    return reply.send(project);
  });

  // Cleanup hook
  app.addHook('onClose', async () => {
    await prisma.$disconnect();
    await pool.end();
  });

  return app;
};
