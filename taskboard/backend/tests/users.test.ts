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
beforeAll(async () => {
  app = await buildServer();
  await app.ready();
  await prisma.user.deleteMany();
});

afterAll(async () => {
  await prisma.$disconnect();
});

test('POST /users should create a new user', async () => {
  const response = await app.inject({
    method: 'POST',
    url: '/users',
    payload: {
      email: 'test@example.com',
      password: 'password123',
      name: 'Test User'
    }
  });

  expect(response.statusCode).toBe(201);
  const data = response.json();
  expect(data.email).toBe('test@example.com');
  expect(data.id).toBeDefined();
  
  // Exclude password from response
  expect(data.password).toBeUndefined();
});
