CREATE TYPE "public"."race_status" AS ENUM('lobby', 'running', 'finished');--> statement-breakpoint
CREATE TABLE "race_participants" (
	"room_id" integer NOT NULL,
	"user_id" text NOT NULL,
	"name" text NOT NULL,
	"joined_at" timestamp with time zone DEFAULT now() NOT NULL,
	"solved_at" timestamp with time zone,
	"attempts" integer DEFAULT 0 NOT NULL,
	CONSTRAINT "race_participants_room_id_user_id_pk" PRIMARY KEY("room_id","user_id")
);
--> statement-breakpoint
CREATE TABLE "race_rooms" (
	"id" serial PRIMARY KEY NOT NULL,
	"code" text NOT NULL,
	"host_id" text NOT NULL,
	"problem_id" integer NOT NULL,
	"difficulty" "difficulty",
	"duration_sec" integer NOT NULL,
	"status" "race_status" DEFAULT 'lobby' NOT NULL,
	"starts_at" timestamp with time zone,
	"ends_at" timestamp with time zone,
	"finished_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "race_rooms_code_unique" UNIQUE("code")
);
--> statement-breakpoint
ALTER TABLE "submissions" ADD COLUMN "race_room_id" integer;--> statement-breakpoint
ALTER TABLE "race_participants" ADD CONSTRAINT "race_participants_room_id_race_rooms_id_fk" FOREIGN KEY ("room_id") REFERENCES "public"."race_rooms"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "race_rooms" ADD CONSTRAINT "race_rooms_problem_id_problems_id_fk" FOREIGN KEY ("problem_id") REFERENCES "public"."problems"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "race_participants_user_idx" ON "race_participants" USING btree ("user_id");--> statement-breakpoint
CREATE INDEX "race_rooms_host_idx" ON "race_rooms" USING btree ("host_id");--> statement-breakpoint
ALTER TABLE "submissions" ADD CONSTRAINT "submissions_race_room_id_race_rooms_id_fk" FOREIGN KEY ("race_room_id") REFERENCES "public"."race_rooms"("id") ON DELETE set null ON UPDATE no action;