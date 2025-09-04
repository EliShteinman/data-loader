-- Insert sample soldier data according to exam requirements
INSERT INTO soldier_details (ID, first_name, last_name, phone_number, rank) VALUES
(301, 'Ahmed', 'Hassan', 5551234, 'Private'),
(302, 'Omar', 'Ali', 5555678, 'Corporal'),
(303, 'Khalid', 'Ibrahim', 5559012, 'Sergeant'),
(304, 'Yusuf', 'Mohamed', 5553456, 'Lieutenant'),
(305, 'Samir', 'Abdullah', 5557890, 'Captain'),
(306, 'Tariq', 'Rashid', 5552468, 'Private'),
(307, 'Nasser', 'Ahmad', 5556802, 'Major'),
(308, 'Hakim', 'Mahmoud', 5551357, 'Colonel');

-- Legacy data for backward compatibility
INSERT INTO data (first_name, last_name) VALUES
('John', 'Doe'),
('Jane', 'Smith'),
('Peter', 'Jones'),
('Emily', 'Williams'),
('Michael', 'Brown'),
('harry', 'potter');