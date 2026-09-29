import "server-only";
import { neon } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-http";
import * as schema from "./schema";

// HTTP driver over the pooled connection: one round trip per query, ideal for serverless.
export const db = drizzle({ client: neon(process.env.DATABASE_URL!), schema });
