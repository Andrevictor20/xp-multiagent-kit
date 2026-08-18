import { test, expect, beforeAll, afterAll } from 'vitest';
import { buildServer } from '../src/app';
import { PrismaPg } from '@prisma/adapter-pg';
import pg from 'pg';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';
import dotenv from 'dotenv';
dotenv.config();

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });
let app: any;
beforeAll(async () => {
  app = await buildServer();
  await app.ready();
  await prisma.user.deleteMany();
  
  const hashedPassword = await bcrypt.hash('password123', 10);
  await prisma.user.create({
    data: {
      email: 'login@example.com',
      password: hashedPassword,
      name: 'Login User'
    }
  });
});

afterAll(async () => {
  await prisma.$disconnect();
});

test('POST /login should return JWT on valid credentials', async () => {
  const response = await app.inject({
    method: 'POST',
    url: '/login',
    payload: {
      email: 'login@example.com',
      password: 'password123'
    }
  });

  expect(response.statusCode).toBe(200);
  const data = response.json();
  expect(data.token).toBeDefined();
});

test('POST /login should return 401 on invalid credentials', async () => {
  const response = await app.inject({
    method: 'POST',
    url: '/login',
    payload: {
      email: 'login@example.com',
      password: 'wrongpassword'
    }
  });

  expect(response.statusCode).toBe(401);
});
