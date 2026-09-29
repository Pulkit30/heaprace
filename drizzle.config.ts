import { defineConfig } from "drizzle-kit";

// Neon writes DATABASE_URL_UNPOOLED to .env.local. Migrations need the direct (non-pooled) connection.
process.loadEnvFile(".env.local");

export default defineConfig({
  dialect: "postgresql",
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dbCredentials: { url: process.env.DATABASE_URL_UNPOOLED! },
  // Only manage our tables; neon_auth belongs to Neon Auth.
  schemaFilter: ["public"],
});
