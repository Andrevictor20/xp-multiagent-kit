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
let userId: string;

beforeAll(async () => {
  app = await buildServer();
  await app.ready();
  await prisma.project.deleteMany();
  await prisma.user.deleteMany();
  
  const user = await prisma.user.create({
    data: {
      email: 'owner@example.com',
      password: 'password123',
      name: 'Owner User'
    }
  });
  userId = user.id;
});

afterAll(async () => {
  await prisma.$disconnect();
});

test('POST /projects should create a new project', async () => {
  const response = await app.inject({
    method: 'POST',
    url: '/projects',
    payload: {
      name: 'Test Project',
      description: 'A test project',
      ownerId: userId
    }
  });

  expect(response.statusCode).toBe(201);
  const data = response.json();
  expect(data.name).toBe('Test Project');
  expect(data.ownerId).toBe(userId);
});
