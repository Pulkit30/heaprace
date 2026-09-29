CREATE TYPE "public"."compare_mode" AS ENUM('exact', 'unordered', 'unordered-deep');--> statement-breakpoint
CREATE TYPE "public"."difficulty" AS ENUM('Easy', 'Medium', 'Hard');--> statement-breakpoint
CREATE TYPE "public"."verdict" AS ENUM('Accepted', 'Wrong Answer', 'Runtime Error', 'Time Limit Exceeded');--> statement-breakpoint
CREATE TABLE "problems" (
	"id" integer PRIMARY KEY NOT NULL,
	"slug" text NOT NULL,
	"title" text NOT NULL,
	"difficulty" "difficulty" NOT NULL,
	"tags" text[] NOT NULL,
	"description" text NOT NULL,
	"examples" jsonb NOT NULL,
	"constraints" text[] NOT NULL,
	"function_name" text NOT NULL,
	"params" text[] NOT NULL,
	"starter_code" text NOT NULL,
	"compare" "compare_mode" NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "problems_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE "submissions" (
	"id" serial PRIMARY KEY NOT NULL,
	"user_id" text NOT NULL,
	"problem_id" integer NOT NULL,
	"language" text DEFAULT 'python' NOT NULL,
	"code" text NOT NULL,
	"verdict" "verdict" NOT NULL,
	"passed" integer NOT NULL,
	"total" integer NOT NULL,
	"runtime_ms" integer NOT NULL,
	"failed_test" integer,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "test_cases" (
	"id" serial PRIMARY KEY NOT NULL,
	"problem_id" integer NOT NULL,
	"position" integer NOT NULL,
	"args" jsonb NOT NULL,
	"expected" jsonb NOT NULL,
	"is_sample" boolean DEFAULT false NOT NULL
);
--> statement-breakpoint
ALTER TABLE "submissions" ADD CONSTRAINT "submissions_problem_id_problems_id_fk" FOREIGN KEY ("problem_id") REFERENCES "public"."problems"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "test_cases" ADD CONSTRAINT "test_cases_problem_id_problems_id_fk" FOREIGN KEY ("problem_id") REFERENCES "public"."problems"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "submissions_user_problem_idx" ON "submissions" USING btree ("user_id","problem_id","created_at");--> statement-breakpoint
CREATE INDEX "submissions_user_created_idx" ON "submissions" USING btree ("user_id","created_at");--> statement-breakpoint
CREATE UNIQUE INDEX "test_cases_problem_position_idx" ON "test_cases" USING btree ("problem_id","position");