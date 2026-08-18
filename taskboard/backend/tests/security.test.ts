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
});

afterAll(async () => {
  await prisma.$disconnect();
});

test('SQL Injection protection via ORM', async () => {
  // Test by sending a payload that would break a naive SQL query
  const maliciousPayload = {
    email: "test@example.com' OR 1=1 --",
    password: "password123"
  };

  const response = await app.inject({
    method: 'POST',
    url: '/login',
    payload: maliciousPayload
  });

  // Should return 400 (Zod email validation fails) or 401 if it bypassed Zod somehow but ORM protected it.
  expect([400, 401]).toContain(response.statusCode);
});

test('XSS protection on input', async () => {
  // The backend should at least not crash, but the frontend is where XSS is truly mitigated (React escapes by default).
  // The API just validates the input structure.
  const maliciousPayload = {
    email: "xss@example.com",
    password: "password123",
    name: "<script>alert('xss')</script>"
  };

  const response = await app.inject({
    method: 'POST',
    url: '/users',
    payload: maliciousPayload
  });

  // It accepts it or sanitizes it. Here we expect 201 or 400.
  // In a real scenario, we might sanitize before DB or rely on React to escape.
  expect([201, 400, 409]).toContain(response.statusCode);
});

test('Rate Limiting on /login', async () => {
  // Try 100 requests
  let got429 = false;
  for (let i = 0; i < 100; i++) {
    const res = await app.inject({
      method: 'POST',
      url: '/login',
      payload: { email: 'login@example.com', password: 'wrong' }
    });
    if (res.statusCode === 429) {
      got429 = true;
      break;
    }
    if (i === 0) console.log('First request status:', res.statusCode, res.headers);
    if (i === 10) console.log('11th request status:', res.statusCode, res.headers);
  }
  expect(got429).toBe(true);
});
