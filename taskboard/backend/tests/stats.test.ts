import { test, expect } from 'vitest';
import { buildServer } from '../src/app';

test('GET /stats should return system stats', async () => {
  const app = await buildServer();
  
  const response = await app.inject({
    method: 'GET',
    url: '/stats'
  });

  expect(response.statusCode).toBe(200);
  const data = JSON.parse(response.payload);
  expect(data).toHaveProperty('users');
  expect(data).toHaveProperty('projects');

  await app.close();
});
