CREATE TABLE "kb_chunks" (
	"id" serial PRIMARY KEY NOT NULL,
	"kind" text NOT NULL,
	"problem_slug" text,
	"pattern_id" text,
	"level" integer,
	"title" text NOT NULL,
	"body" text NOT NULL,
	"search_vector" "tsvector" GENERATED ALWAYS AS (setweight(to_tsvector('english', coalesce(title, '')), 'A') || setweight(to_tsvector('english', coalesce(body, '')), 'B')) STORED
);
--> statement-breakpoint
CREATE INDEX "kb_chunks_search_idx" ON "kb_chunks" USING gin ("search_vector");--> statement-breakpoint
CREATE INDEX "kb_chunks_problem_idx" ON "kb_chunks" USING btree ("problem_slug","kind","level");