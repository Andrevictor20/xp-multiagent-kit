import { test, expect } from 'vitest';
import { buildServer } from '../src/app';

test('health check endpoint should return 200 OK', async () => {
  const app = await buildServer();
  await app.ready();
  
  const response = await app.inject({
    method: 'GET',
    url: '/health'
  });

  expect(response.statusCode).toBe(200);
  expect(response.json()).toEqual({ status: 'ok' });
});
