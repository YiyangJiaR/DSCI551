use Project;
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    head VARCHAR(100)
);

-- Create employees table
CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    email VARCHAR(100),
    hire_date DATE,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Create projects table
CREATE TABLE projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    title VARCHAR(100),
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- Insert sample data into departments
INSERT INTO departments (name, location, head) VALUES
('Human Resources', 'New York - 3F', 'Emily Davis'),
('Engineering', 'San Francisco - 5F', 'John Smith'),
('Sales', 'Chicago - 2F', 'Sarah Johnson'),
('Marketing', 'Los Angeles - 4F', 'Michael Brown');

-- Insert sample data into employees
INSERT INTO employees (name, age, email, hire_date, department_id) VALUES
('Alice Green', 30, 'alice.green@company.com', '2020-03-15', 1),
('Bob White', 27, 'bob.white@company.com', '2021-06-01', 2),
('Charlie Black', 29, 'charlie.black@company.com', '2022-01-20', 2),
('David Blue', 35, 'david.blue@company.com', '2019-10-05', 3),
('Eva Brown', 32, 'eva.brown@company.com', '2021-04-18', 4),
('Frank Stone', 26, 'frank.stone@company.com', '2023-02-10', 2);


-- Insert sample data into projects
INSERT INTO projects (employee_id, title, start_date, end_date) VALUES
(1, 'HR Onboarding Portal', '2022-01-10', '2022-06-30'),
(2, 'Backend Refactoring', '2023-03-01', NULL),
(3, 'Mobile App Frontend', '2023-02-15', '2023-08-01'),
(4, 'Sales CRM Integration', '2021-11-01', '2022-02-28'),
(5, 'Marketing Campaign Analysis', '2023-04-01', NULL),
(6, 'DevOps Pipeline Setup', '2023-05-10', NULL);
