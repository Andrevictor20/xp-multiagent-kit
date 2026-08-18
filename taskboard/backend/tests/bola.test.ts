import { test, expect, beforeAll, afterAll } from 'vitest';
import { buildServer } from '../src/app';
import { PrismaPg } from '@prisma/adapter-pg';
import pg from 'pg';
import { PrismaClient } from '@prisma/client';
import dotenv from 'dotenv';
dotenv.config();

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });
let app: any;
let userAId: string;
let userAToken: string;
let userBToken: string;
let projectAId: string;

beforeAll(async () => {
  app = await buildServer();
  await app.ready();
  await prisma.project.deleteMany();
  await prisma.user.deleteMany();
  
  const userA = await prisma.user.create({
    data: { email: 'a@example.com', password: 'password', name: 'User A' }
  });
  userAId = userA.id;
  userAToken = app.jwt.sign({ id: userA.id, email: userA.email });

  const userB = await prisma.user.create({
    data: { email: 'b@example.com', password: 'password', name: 'User B' }
  });
  userBToken = app.jwt.sign({ id: userB.id, email: userB.email });

  const projectA = await prisma.project.create({
    data: { name: 'Project A', ownerId: userAId }
  });
  projectAId = projectA.id;
});

afterAll(async () => {
  await prisma.$disconnect();
});

test('GET /projects/:id should return 403 or 404 for different user (BOLA/IDOR test)', async () => {
  const response = await app.inject({
    method: 'GET',
    url: `/projects/${projectAId}`,
    headers: {
      Authorization: `Bearer ${userBToken}`
    }
  });

  // Depending on implementation, 403 Forbidden or 404 Not Found is acceptable for BOLA protection.
  expect([403, 404]).toContain(response.statusCode);
});

test('GET /projects/:id should return 200 for owner', async () => {
  const response = await app.inject({
    method: 'GET',
    url: `/projects/${projectAId}`,
    headers: {
      Authorization: `Bearer ${userAToken}`
    }
  });

  expect(response.statusCode).toBe(200);
});
