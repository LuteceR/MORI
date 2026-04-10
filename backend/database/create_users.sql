/* 
    Устарело 
*/
DROP TABLE IF EXISTS users
CREATE TABLE public.users
(
    id serial NOT NULL,
    username character varying(50),
    email character varying(100) NOT NULL,
    password character varying(50) NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.users
    OWNER to postgres;
	
INSERT INTO users(name, email, password) VALUES('kola', 'kola@kola.ko', '12345')
INSERT INTO users(name, email, password) VALUES('lutece', 'lutece@gmail.com', '54321')