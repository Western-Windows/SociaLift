BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "scheduled_posts" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER,
	"message"	VARCHAR,
	"scheduled_time_str"	VARCHAR,
	"fb_post_id"	VARCHAR,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER NOT NULL,
	"username"	VARCHAR,
	"email"	VARCHAR,
	"hashed_password"	VARCHAR NOT NULL,
	"facebook_id"	VARCHAR,
	"fb_access_token"	VARCHAR,
	"fb_page_id"	VARCHAR,
	"fb_page_access_token"	VARCHAR,
	"persona_json"	VARCHAR,
	"is_active"	BOOLEAN,
	PRIMARY KEY("id")
);
INSERT INTO "scheduled_posts" VALUES (1,1,'🌟 Embrace the warmth of comfort with our limited-time gorilla-styled hoodies! 🦍✨ 

Designed to wrap you in care and coziness, these unique hoodies are not just a piece of clothing – they’re an experience. Picture yourself snuggled up, feeling the soft fabric cradle you as you enjoy a quiet evening or a fun day out with friends. 

Each hoodie is crafted with love, ensuring that you not only look good but also feel nurtured and protected. It’s the perfect way to recharge and create memorable moments, whether you’re lounging at home or exploring the great outdoors. 

Don’t miss out on this limited-time offering! Treat yourself or a loved one to the comfort you deserve. 💖✨ #CareAndComfort #GorillaHoodies #SelfCareMoments','2026-06-28T18:39:42.501426','803563356170307_122133268995004757');
INSERT INTO "scheduled_posts" VALUES (2,1,'✨ We''re thrilled to introduce our enchanting new Disney merchandise collection! 🌟 Dive into a world where you can embrace your inner princess and create truly memorable moments. Let us help you nurture that magical experience of joy and self-care. 💖','2026-06-28T18:44:11.070711','803563356170307_122133269337004757');
INSERT INTO "users" VALUES (1,'Youssefproof','youssefproof@gmail.com','$2b$12$qFLUowrif97MK510MprReuh536EbZkUh1ApE3uGyJWtVX.6idQUF6','4030094513803142','EAAPsirfoU5sBR3WEDuJaTOJCu4OzJjxEA9mHb4kEJdo7XrakZCrTMvZAylJVSjZBI9ZBDIYYbMGq0iHpXUAlsQfCR7EGZA4bkowtzY68pcULmlrT4KW5k2kS14r1WC2KuY849tdr2kffgHyQ26BD8qcU0GzRvxfrUQ4cZCovl894VqarWUtLlKjm3DyeqbxlnBgacG3ZBkYh95zfPJZC','803563356170307','EAAPsirfoU5sBR4S58O3y2EUKs01NYVQpLfO0SJA1ZASxO6FuPSgWTbOIMdT5YgZAWTykoWTlo7wucyZCsIK7PjURntuYpyYMyEYVTazrQzG2wvIvOn80E9LpDOp3jrTrFjM0KPFGbp2j6ZAZBbVPmBzTwYF139vvpZA9iRIFypmH44mXdTUWtvATDkgOYOUWVGmKjiNQwCwU5vlLVnkiI5','{"archetype": "The Caregiver", "emotional_tone": "Medium", "keywords": ["comfort", "nurturing", "care", "experience", "memorable"], "voice_description": "A warm and inviting voice that emphasizes comfort and care. Utilizes reassuring language and focuses on the experience of relaxation and recharge, appealing to the audience''s desire for self-care and memorable moments."}',1);
CREATE INDEX IF NOT EXISTS "ix_scheduled_posts_id" ON "scheduled_posts" (
	"id"
);
CREATE INDEX IF NOT EXISTS "ix_scheduled_posts_user_id" ON "scheduled_posts" (
	"user_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "ix_users_email" ON "users" (
	"email"
);
CREATE UNIQUE INDEX IF NOT EXISTS "ix_users_facebook_id" ON "users" (
	"facebook_id"
);
CREATE INDEX IF NOT EXISTS "ix_users_id" ON "users" (
	"id"
);
CREATE INDEX IF NOT EXISTS "ix_users_username" ON "users" (
	"username"
);
COMMIT;
