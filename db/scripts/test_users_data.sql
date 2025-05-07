-- SQL script for filling users table with test data
-- For the users table with columns:
-- id, username, bio, birthday, sex, name, city, rating

-- Clear existing data (optional, comment out if not needed)
-- TRUNCATE TABLE public.users;

-- Insert 100 test users with ages between 18-30 and distributed across 3 cities
INSERT INTO public.users (id, username, bio, birthday, sex, name, city, rating)
VALUES
-- User 1
(1000000001, 'user_alex01', 'Software developer with a passion for AI and machine learning.', '2003-05-15', 'M', 'Alex', 'New York', 4.7),
-- User 2
(1000000002, 'user_emma02', 'Photography enthusiast and travel blogger.', '2002-08-23', 'F', 'Emma', 'Los Angeles', 4.9),
-- User 3
(1000000003, 'user_james03', 'Basketball player and sports fan.', '2001-11-07', 'M', 'James', 'Chicago', 4.5),
-- User 4
(1000000004, 'user_sophia04', 'Book lover and aspiring writer.', '2004-02-19', 'F', 'Sophia', 'New York', 4.8),
-- User 5
(1000000005, 'user_noah05', 'Music producer and electronic music enthusiast.', '2003-07-30', 'M', 'Noah', 'Los Angeles', 4.6),
-- User 6
(1000000006, 'user_olivia06', 'Environmental science student and climate activist.', '2002-04-12', 'F', 'Olivia', 'Chicago', 4.7),
-- User 7
(1000000007, 'user_william07', 'Tech startup founder and entrepreneur.', '2001-09-25', 'M', 'William', 'New York', 4.9),
-- User 8
(1000000008, 'user_ava08', 'Yoga instructor and wellness advocate.', '2005-01-08', 'F', 'Ava', 'Los Angeles', 4.8),
-- User 9
(1000000009, 'user_ethan09', 'Financial analyst and cryptocurrency investor.', '2004-06-17', 'M', 'Ethan', 'Chicago', 4.5),
-- User 10
(1000000010, 'user_mia10', 'Digital artist and graphic designer.', '2003-03-29', 'F', 'Mia', 'New York', 4.7),
-- User 11
(1000000011, 'user_jacob11', 'Culinary arts student and food blogger.', '2002-12-05', 'M', 'Jacob', 'Los Angeles', 4.6),
-- User 12
(1000000012, 'user_charlotte12', 'Fashion design student with focus on sustainable clothing.', '2001-10-14', 'F', 'Charlotte', 'Chicago', 4.8),
-- User 13
(1000000013, 'user_michael13', 'Video game developer and esports enthusiast.', '2005-08-02', 'M', 'Michael', 'New York', 4.5),
-- User 14
(1000000014, 'user_amelia14', 'Marine biology student interested in ocean conservation.', '2004-05-21', 'F', 'Amelia', 'Los Angeles', 4.7),
-- User 15
(1000000015, 'user_benjamin15', 'Architecture student focusing on sustainable design.', '2003-02-11', 'M', 'Benjamin', 'Chicago', 4.6),
-- User 16
(1000000016, 'user_evelyn16', 'Psychology student interested in child development.', '2002-11-30', 'F', 'Evelyn', 'New York', 4.9),
-- User 17
(1000000017, 'user_daniel17', 'Civil engineering student working on infrastructure projects.', '2001-07-19', 'M', 'Daniel', 'Los Angeles', 4.5),
-- User 18
(1000000018, 'user_harper18', 'Journalism student covering campus politics.', '2005-09-08', 'F', 'Harper', 'Chicago', 4.8),
-- User 19
(1000000019, 'user_matthew19', 'Physics student researching quantum mechanics.', '2004-04-27', 'M', 'Matthew', 'New York', 4.7),
-- User 20
(1000000020, 'user_liz20', 'Veterinary medicine student specializing in exotic animals.', '2003-01-16', 'F', 'Elizabeth', 'Los Angeles', 4.6),
-- User 21
(1000000021, 'user_joseph21', 'Marketing student with interest in digital strategies.', '2002-10-03', 'M', 'Joseph', 'Chicago', 4.5),
-- User 22
(1000000022, 'user_sofia22', 'Interior design student with a minimalist approach.', '2001-07-22', 'F', 'Sofia', 'New York', 4.8),
-- User 23
(1000000023, 'user_david23', 'Data science student working in healthcare analytics.', '2005-03-11', 'M', 'David', 'Los Angeles', 4.7),
-- User 24
(1000000024, 'user_victoria24', 'Nutrition student promoting plant-based diets.', '2004-12-28', 'F', 'Victoria', 'Chicago', 4.9),
-- User 25
(1000000025, 'user_andrew25', 'Photography student specializing in wildlife.', '2003-05-07', 'M', 'Andrew', 'New York', 4.6),
-- User 26
(1000000026, 'user_grace26', 'Dance student teaching contemporary styles.', '2002-02-14', 'F', 'Grace', 'Los Angeles', 4.7),
-- User 27
(1000000027, 'user_joshua27', 'Finance student with a focus on green investments.', '2001-11-23', 'M', 'Joshua', 'Chicago', 4.5),
-- User 28
(1000000028, 'user_chloe28', 'Speech therapy student working with children.', '2005-06-09', 'F', 'Chloe', 'New York', 4.8),
-- User 29
(1000000029, 'user_chris29', 'Aerospace engineering student designing aircraft.', '2004-01-31', 'M', 'Christopher', 'Los Angeles', 4.7),
-- User 30
(1000000030, 'user_zoey30', 'Film student focusing on documentaries.', '2003-08-18', 'F', 'Zoey', 'Chicago', 4.6),
-- User 31
(1000000031, 'user_samuel31', 'Cybersecurity student protecting digital assets.', '2002-05-27', 'M', 'Samuel', 'New York', 4.5),
-- User 32
(1000000032, 'user_audrey32', 'Linguistics student studying multiple languages.', '2001-12-14', 'F', 'Audrey', 'Los Angeles', 4.8),
-- User 33
(1000000033, 'user_john33', 'Mechanical engineering student building robots.', '2005-07-03', 'M', 'John', 'Chicago', 4.7),
-- User 34
(1000000034, 'user_lily34', 'Art history student with focus on Renaissance period.', '2004-04-20', 'F', 'Lily', 'New York', 4.9),
-- User 35
(1000000035, 'user_ryan35', 'Computer science student developing mobile apps.', '2003-11-09', 'M', 'Ryan', 'Los Angeles', 4.6),
-- User 36
(1000000036, 'user_hannah36', 'Sociology student researching urban communities.', '2002-08-26', 'F', 'Hannah', 'Chicago', 4.7),
-- User 37
(1000000037, 'user_nathan37', 'Political science student interested in international relations.', '2001-05-15', 'M', 'Nathan', 'New York', 4.5),
-- User 38
(1000000038, 'user_zoe38', 'Biochemistry student researching new medicines.', '2005-02-02', 'F', 'Zoe', 'Los Angeles', 4.8),
-- User 39
(1000000039, 'user_isaac39', 'Economics student focusing on behavioral economics.', '2004-09-19', 'M', 'Isaac', 'Chicago', 4.7),
-- User 40
(1000000040, 'user_leah40', 'Nursing student specializing in pediatric care.', '2003-06-08', 'F', 'Leah', 'New York', 4.6),
-- User 41
(1000000041, 'user_luke41', 'History student focusing on ancient civilizations.', '2002-03-25', 'M', 'Luke', 'Los Angeles', 4.5),
-- User 42
(1000000042, 'user_stella42', 'Astronomy student observing distant galaxies.', '2001-12-12', 'F', 'Stella', 'Chicago', 4.8),
-- User 43
(1000000043, 'user_owen43', 'Geology student studying volcanic activity.', '2005-09-29', 'M', 'Owen', 'New York', 4.7),
-- User 44
(1000000044, 'user_natalie44', 'Anthropology student researching indigenous cultures.', '2004-06-16', 'F', 'Natalie', 'Los Angeles', 4.9),
-- User 45
(1000000045, 'user_gabriel45', 'Philosophy student exploring existentialism.', '2003-03-05', 'M', 'Gabriel', 'Chicago', 4.6),
-- User 46
(1000000046, 'user_savannah46', 'Botany student studying medicinal plants.', '2002-12-22', 'F', 'Savannah', 'New York', 4.7),
-- User 47
(1000000047, 'user_jon47', 'Electrical engineering student building renewable energy systems.', '2001-09-11', 'M', 'Jonathan', 'Los Angeles', 4.5),
-- User 48
(1000000048, 'user_bella48', 'Theater student performing in classical plays.', '2005-06-28', 'F', 'Bella', 'Chicago', 4.8),
-- User 49
(1000000049, 'user_adam49', 'Kinesiology student specializing in sports medicine.', '2004-03-17', 'M', 'Adam', 'New York', 4.7),
-- User 50
(1000000050, 'user_claire50', 'Music student composing original pieces.', '2003-12-04', 'F', 'Claire', 'Los Angeles', 4.6),
-- User 51
(1000000051, 'user_aaron51', 'Chemical engineering student developing eco-friendly materials.', '2002-09-21', 'M', 'Aaron', 'Chicago', 4.5),
-- User 52
(1000000052, 'user_skylar52', 'Education student focusing on special needs teaching.', '2001-06-10', 'F', 'Skylar', 'New York', 4.8),
-- User 53
(1000000053, 'user_ian53', 'Urban planning student designing sustainable cities.', '2005-03-27', 'M', 'Ian', 'Los Angeles', 4.7),
-- User 54
(1000000054, 'user_julia54', 'Dental student promoting preventive care.', '2004-12-14', 'F', 'Julia', 'Chicago', 4.9),
-- User 55
(1000000055, 'user_jason55', 'Criminology student studying forensic science.', '2003-09-03', 'M', 'Jason', 'New York', 4.6),
-- User 56
(1000000056, 'user_alice56', 'Public health student focusing on epidemiology.', '2002-06-20', 'F', 'Alice', 'Los Angeles', 4.7),
-- User 57
(1000000057, 'user_eric57', 'Biotechnology student working on genetic research.', '2001-03-09', 'M', 'Eric', 'Chicago', 4.5),
-- User 58
(1000000058, 'user_maddy58', 'International business student studying global markets.', '2005-12-26', 'F', 'Madeline', 'New York', 4.8),
-- User 59
(1000000059, 'user_brian59', 'Information technology student specializing in cloud computing.', '2004-09-15', 'M', 'Brian', 'Los Angeles', 4.7),
-- User 60
(1000000060, 'user_hazel60', 'Occupational therapy student helping rehabilitation patients.', '2003-06-02', 'F', 'Hazel', 'Chicago', 4.6),
-- User 61
(1000000061, 'user_kyle61', 'Hospitality management student with focus on sustainable tourism.', '2002-03-19', 'M', 'Kyle', 'New York', 4.5),
-- User 62
(1000000062, 'user_eleanor62', 'Creative writing student working on first novel.', '2001-12-06', 'F', 'Eleanor', 'Los Angeles', 4.8),
-- User 63
(1000000063, 'user_tyler63', 'Sports management student organizing campus events.', '2005-09-23', 'M', 'Tyler', 'Chicago', 4.7),
-- User 64
(1000000064, 'user_violet64', 'Dietetics student promoting balanced nutrition.', '2004-06-12', 'F', 'Violet', 'New York', 4.9),
-- User 65
(1000000065, 'user_brandon65', 'Journalism student focusing on investigative reporting.', '2003-03-01', 'M', 'Brandon', 'Los Angeles', 4.6),
-- User 66
(1000000066, 'user_penny66', 'Graphic design student creating digital illustrations.', '2002-11-18', 'F', 'Penelope', 'Chicago', 4.7),
-- User 67
(1000000067, 'user_zach67', 'Environmental engineering student developing water purification systems.', '2001-08-07', 'M', 'Zachary', 'New York', 4.5),
-- User 68
(1000000068, 'user_ruby68', 'Physical therapy student specializing in sports injuries.', '2005-05-24', 'F', 'Ruby', 'Los Angeles', 4.8),
-- User 69
(1000000069, 'user_caleb69', 'Astronomy student mapping celestial bodies.', '2004-02-11', 'M', 'Caleb', 'Chicago', 4.7),
-- User 70
(1000000070, 'user_aubrey70', 'Neuroscience student studying brain development.', '2003-11-28', 'F', 'Aubrey', 'New York', 4.6),
-- User 71
(1000000071, 'user_dylan71', 'Law student focusing on environmental law.', '2002-08-15', 'M', 'Dylan', 'Los Angeles', 4.5),
-- User 72
(1000000072, 'user_piper72', 'Culinary arts student specializing in pastry.', '2001-05-04', 'F', 'Piper', 'Chicago', 4.8),
-- User 73
(1000000073, 'user_carter73', 'Robotics student building autonomous drones.', '2005-02-21', 'M', 'Carter', 'New York', 4.7),
-- User 74
(1000000074, 'user_quinn74', 'Linguistics student studying ancient languages.', '2004-11-10', 'F', 'Quinn', 'Los Angeles', 4.9),
-- User 75
(1000000075, 'user_levi75', 'Marine biology student researching coral reefs.', '2003-08-29', 'M', 'Levi', 'Chicago', 4.6),
-- User 76
(1000000076, 'user_isla76', 'Fashion merchandising student studying sustainable fashion.', '2002-05-18', 'F', 'Isla', 'New York', 4.7),
-- User 77
(1000000077, 'user_jaxon77', 'Computer engineering student developing AI algorithms.', '2001-02-07', 'M', 'Jaxon', 'Los Angeles', 4.5),
-- User 78
(1000000078, 'user_nova78', 'Astronomy student studying exoplanets.', '2005-11-24', 'F', 'Nova', 'Chicago', 4.8),
-- User 79
(1000000079, 'user_leo79', 'Film production student directing short films.', '2004-08-13', 'M', 'Leo', 'New York', 4.7),
-- User 80
(1000000080, 'user_willow80', 'Environmental science student studying climate change.', '2003-05-02', 'F', 'Willow', 'Los Angeles', 4.6),
-- User 81
(1000000081, 'user_hudson81', 'Business administration student focusing on entrepreneurship.', '2002-01-21', 'M', 'Hudson', 'Chicago', 4.5),
-- User 82
(1000000082, 'user_ivy82', 'Dance student specializing in contemporary dance.', '2001-10-10', 'F', 'Ivy', 'New York', 4.8),
-- User 83
(1000000083, 'user_axel83', 'Mechanical engineering student designing renewable energy systems.', '2005-07-29', 'M', 'Axel', 'Los Angeles', 4.7),
-- User 84
(1000000084, 'user_luna84', 'Psychology student researching cognitive development.', '2004-04-17', 'F', 'Luna', 'Chicago', 4.9),
-- User 85
(1000000085, 'user_silas85', 'Architecture student designing sustainable buildings.', '2003-01-06', 'M', 'Silas', 'New York', 4.6),
-- User 86
(1000000086, 'user_ember86', 'Art student focusing on digital media.', '2002-10-25', 'F', 'Ember', 'Los Angeles', 4.7),
-- User 87
(1000000087, 'user_felix87', 'Physics student researching particle physics.', '2001-07-14', 'M', 'Felix', 'Chicago', 4.5),
-- User 88
(1000000088, 'user_aurora88', 'Literature student studying comparative literature.', '2005-04-03', 'F', 'Aurora', 'New York', 4.8),
-- User 89
(1000000089, 'user_miles89', 'Music production student creating electronic music.', '2004-12-22', 'M', 'Miles', 'Los Angeles', 4.7),
-- User 90
(1000000090, 'user_autumn90', 'Nutrition student focusing on sports nutrition.', '2003-09-11', 'F', 'Autumn', 'Chicago', 4.6),
-- User 91
(1000000091, 'user_rowan91', 'Environmental engineering student working on water conservation.', '2002-06-30', 'M', 'Rowan', 'New York', 4.5),
-- User 92
(1000000092, 'user_sage92', 'Botany student researching medicinal plants.', '2001-03-19', 'F', 'Sage', 'Los Angeles', 4.8),
-- User 93
(1000000093, 'user_jasper93', 'Geology student studying seismic activity.', '2005-12-08', 'M', 'Jasper', 'Chicago', 4.7),
-- User 94
(1000000094, 'user_iris94', 'Photography student specializing in portrait photography.', '2004-09-27', 'F', 'Iris', 'New York', 4.9),
-- User 95
(1000000095, 'user_finn95', 'Marine science student studying ocean conservation.', '2003-06-16', 'M', 'Finn', 'Los Angeles', 4.6),
-- User 96
(1000000096, 'user_nova96', 'Astrophysics student researching black holes.', '2002-03-05', 'F', 'Nova', 'Chicago', 4.7),
-- User 97
(1000000097, 'user_kai97', 'Oceanography student studying marine ecosystems.', '2001-12-24', 'M', 'Kai', 'New York', 4.5),
-- User 98
(1000000098, 'user_eden98', 'Sustainable agriculture student developing urban farming techniques.', '2005-09-13', 'F', 'Eden', 'Los Angeles', 4.8),
-- User 99
(1000000099, 'user_river99', 'Environmental policy student advocating for climate action.', '2004-06-02', 'M', 'River', 'Chicago', 4.7),
-- User 100
(1000000100, 'user_willow100', 'Conservation biology student protecting endangered species.', '2003-02-21', 'F', 'Willow', 'New York', 4.6);
