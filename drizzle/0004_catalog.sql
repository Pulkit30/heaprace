ALTER TYPE "public"."compare_mode" ADD VALUE 'approx';--> statement-breakpoint
ALTER TABLE "problems" ADD COLUMN "out_arg" integer;--> statement-breakpoint
ALTER TABLE "problems" ADD COLUMN "design" boolean DEFAULT false NOT NULL;--> statement-breakpoint
ALTER TABLE "problems" ADD COLUMN "pattern_id" text DEFAULT 'arrays-hashing' NOT NULL;