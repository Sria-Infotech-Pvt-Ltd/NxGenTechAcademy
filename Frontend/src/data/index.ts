import { GraduationCap, Code, Database, Terminal, Monitor, Brain, Presentation, Globe, Search, BarChart } from "lucide-react";
import { Category, Course, Instructor, StudyMaterial } from "./types";

// Top-level categories (groups). The UI will show these categories and courses will be grouped into them.
export const categories: Category[] = [
  { id: "all", name: "All Categories" },
  { id: "python", name: "Python" },
  { id: "aiml", name: "AI & ML" },
  // { id: "mobile-app", name: "Mobile App Development" },
  // { id: "fullstack", name: "Full Stack" },
  // { id: "ai-data-science", name: "AI Data Science" },
  // { id: "python-ai-dsa", name: "Python Full stack AI integration & DSA" },
  // { id: "powerbi", name: "Power BI full stack" },
  // { id: "testing", name: "Testing tools" },
  // { id: "cybersecurity", name: "Cybersecurity" },
  // { id: "sap", name: "SAP" }
];

// Mapping from the existing course.category values to the new top-level category ids
const courseCategoryToGroup: Record<string, string> = {
  fullstack: "fullstack",
  web: "fullstack",      // Web Dev with fullstack focus
  spring: "fullstack",
  microservices: "fullstack",

  // Common JS / frontend / backend labels often used by instructors
  reactjs: "fullstack",
  nodejs: "fullstack",
  mern: "fullstack",
  uiux: "fullstack",
  php: "fullstack",

  python: "python-ai-dsa",
  django: "python-ai-dsa",
  ai: "python-ai-dsa",
  dsa: "python-ai-dsa",

  powerbi: "powerbi",
  analytics: "powerbi",
  tableau: "powerbi",
  excel: "powerbi",

  data: "ai-data-science",
  machinelearning: "ai-data-science",
  deeplearning: "ai-data-science",
  nlp: "ai-data-science",

  testing: "testing",
  selenium: "testing",
  automation: "testing",
  qa: "testing",

  security: "cybersecurity",
  pentesting: "cybersecurity",
  ethical: "cybersecurity",
  forensics: "cybersecurity",
};

export const studyMaterials: ReadonlyArray<StudyMaterial> = [
  {
    id: 1,
    title: "Frontend Web Development",
    subject: "web",
    description: "Master HTML, CSS, JavaScript, React and modern frontend development techniques.",
    pages: "120 Pages",
    format: "PDF",
    size: "15 MB",
    image: "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=800&h=400&fit=crop",
    chapters: [
      {
        title: "HTML5 and CSS3 Fundamentals",
        duration: "4 hours",
        topics: ["Semantic HTML", "Flexbox", "CSS Grid", "Responsive Design"],
        difficulty: "Beginner"
      },
      {
        title: "JavaScript Essentials",
        duration: "6 hours",
        topics: ["ES6+", "Promises", "Async/Await", "DOM Manipulation"],
        difficulty: "Intermediate"
      },
      {
        title: "React Fundamentals",
        duration: "8 hours",
        topics: ["Components", "Props", "State", "Hooks"],
        difficulty: "Intermediate"
      },
      {
        title: "State Management",
        duration: "5 hours",
        topics: ["Context API", "Redux", "Zustand", "State Patterns"],
        difficulty: "Advanced"
      },
      {
        title: "Performance Optimization",
        duration: "4 hours",
        topics: ["Code Splitting", "Lazy Loading", "Memoization", "Bundle Analysis"],
        difficulty: "Advanced"
      },
      {
        title: "Testing and Deployment",
        duration: "5 hours",
        topics: ["Jest", "React Testing Library", "CI/CD", "Vercel Deployment"],
        difficulty: "Advanced"
      }
    ]
  },
  {
    id: 2,
    title: "UI/UX Design",
    subject: "web",
    description: "Learn user interface design, user experience principles, and design tools like Figma.",
    pages: "150 Pages",
    format: "PDF",
    size: "18 MB",
    image: "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&h=400&fit=crop",
    chapters: [
      {
        title: "Dart Programming",
        duration: "5 hours",
        topics: ["Syntax", "OOP", "Async Programming", "Collections"],
        difficulty: "Beginner"
      },
      {
        title: "Flutter Widgets",
        duration: "8 hours",
        topics: ["Material Design", "Custom Widgets", "Layouts", "Navigation"],
        difficulty: "Intermediate"
      },
      {
        title: "State Management",
        duration: "6 hours",
        topics: ["Provider", "Riverpod", "Bloc Pattern", "GetX"],
        difficulty: "Advanced"
      },
      {
        title: "API Integration",
        duration: "4 hours",
        topics: ["REST APIs", "GraphQL", "WebSockets", "Local Storage"],
        difficulty: "Intermediate"
      },
      {
        title: "Platform Integration",
        duration: "5 hours",
        topics: ["Native Features", "Camera", "Location", "Notifications"],
        difficulty: "Advanced"
      },
      {
        title: "App Publishing",
        duration: "4 hours",
        topics: ["App Store", "Play Store", "CI/CD", "Analytics"],
        difficulty: "Advanced"
      }
    ]
  },
  {
    id: 3,
    title: "Flutter Mobile Development",
    subject: "mobile",
    description: "Build cross-platform mobile apps with Flutter and Dart programming language.",
    pages: "130 Pages",
    format: "PDF",
    size: "16 MB",
    image: "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&h=400&fit=crop",
    chapters: [
      {
        title: "Dart Programming",
        duration: "6 hours",
        topics: ["Syntax", "OOP", "Async Programming", "Collections"],
        difficulty: "Beginner"
      },
      {
        title: "Flutter Widgets",
        duration: "7 hours",
        topics: ["Material Design", "Custom Widgets", "Layouts", "Navigation"],
        difficulty: "Intermediate"
      },
      {
        title: "State Management",
        duration: "8 hours",
        topics: ["Provider", "Bloc", "GetX", "State Patterns"],
        difficulty: "Advanced"
      },
      {
        title: "API Integration",
        duration: "5 hours",
        topics: ["REST APIs", "GraphQL", "Local Storage", "Caching"],
        difficulty: "Advanced"
      },
      {
        title: "Platform Features",
        duration: "6 hours",
        topics: ["Camera", "Location", "Notifications", "Permissions"],
        difficulty: "Advanced"
      },
      {
        title: "App Publishing",
        duration: "4 hours",
        topics: ["App Store", "Play Store", "CI/CD", "Analytics"],
        difficulty: "Expert"
      }
    ]
  },
  {
    id: 4,
    title: "iOS App Development",
    subject: "mobile",
    description: "Create native iOS applications using Swift and SwiftUI framework.",
    pages: "140 Pages",
    format: "PDF",
    size: "19 MB",
    image: "https://images.unsplash.com/photo-1537498425277-c283d32ef9db?w=800&h=400&fit=crop",
    chapters: [
      {
        title: "Swift Fundamentals",
        duration: "6 hours",
        topics: ["Swift Syntax", "Optionals", "Collections", "Functions"],
        difficulty: "Beginner"
      },
      {
        title: "SwiftUI Basics",
        duration: "7 hours",
        topics: ["Views", "Modifiers", "Layout", "Navigation"],
        difficulty: "Intermediate"
      },
      {
        title: "Data & State",
        duration: "8 hours",
        topics: ["State", "Binding", "ObservableObject", "Environment"],
        difficulty: "Advanced"
      },
      {
        title: "iOS Features",
        duration: "6 hours",
        topics: ["CoreData", "Networking", "Maps", "Notifications"],
        difficulty: "Advanced"
      },
      {
        title: "Advanced UI",
        duration: "7 hours",
        topics: ["Animations", "Custom Views", "Gestures", "Accessibility"],
        difficulty: "Advanced"
      },
      {
        title: "App Store",
        duration: "4 hours",
        topics: ["Testing", "Distribution", "App Review", "Analytics"],
        difficulty: "Expert"
      }
    ]
  },
  {
    id: 5,
    title: "Node.js Backend Development",
    subject: "backend",
    description: "Build scalable server-side applications with Node.js, Express, and MongoDB.",
    pages: "120 Pages",
    format: "PDF",
    size: "15 MB",
    image: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&h=400&fit=crop",
    chapters: [
      {
        title: "Node.js Basics",
        duration: "5 hours",
        topics: ["Event Loop", "Modules", "NPM", "Express"],
        difficulty: "Beginner"
      },
      {
        title: "Express Framework",
        duration: "6 hours",
        topics: ["Routing", "Middleware", "Error Handling", "Security"],
        difficulty: "Intermediate"
      },
      {
        title: "MongoDB",
        duration: "7 hours",
        topics: ["CRUD", "Mongoose", "Aggregation", "Indexing"],
        difficulty: "Advanced"
      },
      {
        title: "Authentication",
        duration: "5 hours",
        topics: ["JWT", "OAuth", "Sessions", "Security"],
        difficulty: "Advanced"
      },
      {
        title: "API Design",
        duration: "6 hours",
        topics: ["REST", "GraphQL", "Documentation", "Testing"],
        difficulty: "Advanced"
      },
      {
        title: "Deployment",
        duration: "4 hours",
        topics: ["Docker", "CI/CD", "Cloud", "Monitoring"],
        difficulty: "Expert"
      }
    ]
  },
  {
    id: 6,
    title: "Python Django Development",
    subject: "backend",
    description: "Master backend development with Python Django framework and PostgreSQL.",
    pages: "125 Pages",
    format: "PDF",
    size: "17 MB",
    image: "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=800&h=400&fit=crop",
    chapters: [
      {
        title: "Django Basics",
        duration: "5 hours",
        topics: ["MVT Pattern", "URLs", "Views", "Templates"],
        difficulty: "Beginner"
      },
      {
        title: "Models & ORM",
        duration: "7 hours",
        topics: ["Models", "Queries", "Migrations", "Admin"],
        difficulty: "Intermediate"
      },
      {
        title: "Forms & Auth",
        duration: "6 hours",
        topics: ["Forms", "Validation", "Authentication", "Permissions"],
        difficulty: "Advanced"
      },
      {
        title: "REST APIs",
        duration: "5 hours",
        topics: ["DRF", "Serializers", "ViewSets", "Authentication"],
        difficulty: "Advanced"
      },
      {
        title: "Advanced Django",
        duration: "8 hours",
        topics: ["Signals", "Middleware", "Caching", "Celery"],
        difficulty: "Advanced"
      },
      {
        title: "Deployment",
        duration: "4 hours",
        topics: ["Gunicorn", "Nginx", "PostgreSQL", "Docker"],
        difficulty: "Expert"
      }
    ]
  },
  {
    id: 7,
    title: "Data Analytics with Python",
    subject: "data",
    description: "Learn data analysis using Python, Pandas, NumPy, and data visualization tools.",
    pages: "140 Pages",
    format: "PDF",
    size: "20 MB",
    image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=400&fit=crop",
    chapters: [
      {
        title: "Python Basics",
        duration: "5 hours",
        topics: ["NumPy", "Pandas", "Data Types", "Functions"],
        difficulty: "Beginner"
      },
      {
        title: "Data Cleaning",
        duration: "6 hours",
        topics: ["Missing Data", "Outliers", "Transformation", "Validation"],
        difficulty: "Intermediate"
      },
      {
        title: "Visualization",
        duration: "7 hours",
        topics: ["Matplotlib", "Seaborn", "Plotly", "Dashboards"],
        difficulty: "Intermediate"
      },
      {
        title: "Statistics",
        duration: "8 hours",
        topics: ["Descriptive", "Inferential", "Hypothesis", "Regression"],
        difficulty: "Advanced"
      },
      {
        title: "Machine Learning",
        duration: "10 hours",
        topics: ["Scikit-learn", "Models", "Evaluation", "Pipeline"],
        difficulty: "Advanced"
      },
      {
        title: "Big Data",
        duration: "6 hours",
        topics: ["Spark", "Hadoop", "Cloud Tools", "Deployment"],
        difficulty: "Expert"
      }
    ]
  },
  {
    id: 8,
    title: "Business Intelligence & SQL",
    subject: "data",
    description: "Learn SQL, Power BI, and advanced data analysis techniques for business insights.",
    pages: "110 Pages",
    format: "PDF",
    size: "16 MB",
    image: "https://images.unsplash.com/photo-1543286386-713bdd548da4?w=800&h=400&fit=crop",
    chapters: [
      {
        title: "SQL Fundamentals",
        duration: "6 hours",
        topics: ["Queries", "Joins", "Aggregations", "Subqueries"],
        difficulty: "Beginner"
      },
      {
        title: "Data Modeling",
        duration: "5 hours",
        topics: ["Schema Design", "Normalization", "Relationships", "Keys"],
        difficulty: "Intermediate"
      },
      {
        title: "Power BI Basics",
        duration: "7 hours",
        topics: ["Data Import", "Transformations", "DAX", "Visuals"],
        difficulty: "Intermediate"
      },
      {
        title: "Advanced Analytics",
        duration: "8 hours",
        topics: ["Measures", "Calculations", "Time Intelligence", "KPIs"],
        difficulty: "Advanced"
      },
      {
        title: "Dashboard Design",
        duration: "6 hours",
        topics: ["Layout", "Interactivity", "Best Practices", "Sharing"],
        difficulty: "Advanced"
      },
      {
        title: "Enterprise BI",
        duration: "4 hours",
        topics: ["Security", "Gateway", "Deployment", "Administration"],
        difficulty: "Expert"
      }
    ]
  },
  {
    id: 9,
    title: "SAP ABAP Development",
    subject: "sap",
    description: "Master SAP ABAP programming and enterprise system development.",
    pages: "160 Pages",
    format: "PDF",
    size: "22 MB",
    image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=400&fit=crop",
    chapters: [
      {
        title: "ABAP Basics",
        duration: "6 hours",
        topics: ["Syntax", "Data Types", "Control Flow", "Forms"],
        difficulty: "Beginner"
      },
      {
        title: "OO ABAP",
        duration: "8 hours",
        topics: ["Classes", "Interfaces", "Events", "Exceptions"],
        difficulty: "Intermediate"
      },
      {
        title: "Database",
        duration: "7 hours",
        topics: ["OpenSQL", "Native SQL", "BOPF", "CDS Views"],
        difficulty: "Advanced"
      },
      {
        title: "UI Development",
        duration: "6 hours",
        topics: ["Dynpro", "Web Dynpro", "Fiori", "UI5"],
        difficulty: "Advanced"
      },
      {
        title: "Integration",
        duration: "8 hours",
        topics: ["RFC", "BAPI", "Web Services", "Cloud"],
        difficulty: "Advanced"
      },
      {
        title: "Security",
        duration: "5 hours",
        topics: ["Authorization", "Roles", "Auditing", "Compliance"],
        difficulty: "Expert"
      }
    ]
  },
  {
    id: 10,
    title: "SAP HANA Development",
    subject: "sap",
    description: "Learn SAP HANA development, modeling, and implementation techniques.",
    pages: "145 Pages",
    format: "PDF",
    size: "18 MB",
    image: "https://images.unsplash.com/photo-1537432376769-00f5c2f4c8d2?w=800&h=400&fit=crop",
    chapters: [
      {
        title: "HANA Basics",
        duration: "5 hours",
        topics: ["Architecture", "Studio", "Tables", "Views"],
        difficulty: "Beginner"
      },
      {
        title: "Data Modeling",
        duration: "7 hours",
        topics: ["Attributes", "Calculations", "Associations", "Hierarchies"],
        difficulty: "Intermediate"
      },
      {
        title: "SQLScript",
        duration: "8 hours",
        topics: ["Procedures", "Functions", "Libraries", "Optimization"],
        difficulty: "Advanced"
      },
      {
        title: "XS Advanced",
        duration: "6 hours",
        topics: ["MTA", "Services", "Security", "UI"],
        difficulty: "Advanced"
      },
      {
        title: "Integration",
        duration: "7 hours",
        topics: ["ERP", "BW", "S/4HANA", "Cloud"],
        difficulty: "Advanced"
      },
      {
        title: "Administration",
        duration: "5 hours",
        topics: ["Monitoring", "Backup", "Security", "Migration"],
        difficulty: "Expert"
      }
    ]
  }
];

// Categories defined above

export const instructors: Instructor[] = [
  {
    id: 1,
    name: "Dr. Rajesh Kumar",
    role: "Lead Java Architect",
    category: "fullstack",
    company: "Oracle",
    designation: "Principal Java Developer",
    experience: "15+ years",
    image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop",
    description: "Expert in Java enterprise applications with extensive experience in Spring Boot, Microservices, and Cloud Architecture. Oracle certified instructor and frequent conference speaker.",
  },
  {
    id: 2,
    name: "Sarah Wilson",
    role: "Python Full Stack Expert",
    category: "python-ai-dsa",
    company: "Google",
    designation: "Senior Software Engineer",
    experience: "10+ years",
    image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop",
    description: "Python specialist with expertise in Django, Flask, and modern web frameworks. Google Developer Expert who has contributed to major open-source projects.",
  },
  {
    id: 3,
    name: "Mohammed Ali",
    role: "MERN Stack Lead",
    category: "fullstack",
    company: "Meta",
    designation: "Technical Architect",
    experience: "12+ years",
    image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop",
    description: "Full stack developer specializing in MongoDB, Express.js, React, and Node.js. Created multiple successful web applications and mentored dozens of developers.",
  },
  {
    id: 4,
    name: "Emily Chen",
    role: "UI/UX Design Lead",
    category: "fullstack",
    company: "Apple",
    designation: "Senior UX Designer",
    experience: "8+ years",
    image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop",
    description: "Award-winning UI/UX designer with expertise in user research, interaction design, and design systems. Previously designed interfaces for major tech companies.",
  },
  {
    id: 5,
    name: "David Rodriguez",
    role: "React Expert",
    category: "fullstack",
    company: "Amazon",
    designation: "Senior Frontend Engineer",
    experience: "9+ years",
    image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop",
    description: "React specialist focused on building scalable front-end architectures. Created popular open-source React libraries and mentors junior developers.",
  },
  {
    id: 6,
    name: "Jessica Thompson",
    role: "Node.js Expert",
    category: "fullstack",
    company: "Microsoft",
    designation: "Lead Backend Developer",
    experience: "11+ years",
    image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=400&fit=crop",
    description: "Node.js expert specializing in scalable backend architectures. Microsoft MVP with extensive experience in real-time applications and microservices.",
  },
  {
    id: 7,
    name: "Michael Zhang",
    role: "Web Design Specialist",
    category: "fullstack",
    company: "Adobe",
    designation: "Creative Director",
    experience: "13+ years",
    image: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=400&fit=crop",
    description: "Creative professional with deep knowledge of web design principles, responsive design, and modern CSS frameworks. Adobe certified expert in web technologies.",
  },
  {
    id: 8,
    name: "Lisa Patel",
    role: "PHP & MySQL Expert",
    category: "fullstack",
    company: "LinkedIn",
    designation: "Technical Lead",
    experience: "10+ years",
    image: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop",
    description: "Full stack PHP developer with expertise in Laravel, Symfony, and database optimization. Created multiple high-traffic web applications.",
  },
  {
    id: 9,
    name: "John Anderson",
    role: "Digital Marketing Strategist",
    category: "fullstack",
    company: "HubSpot",
    designation: "Marketing Director",
    experience: "14+ years",
    image: "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=400&h=400&fit=crop",
    description: "Digital marketing expert with comprehensive knowledge of SEO, content marketing, and social media strategies. Google certified professional.",
  },
  {
    id: 10,
    name: "Anna Martinez",
    role: "Django Framework Expert",
    category: "python-ai-dsa",
    company: "Instagram",
    designation: "Senior Backend Engineer",
    experience: "9+ years",
    image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=400&fit=crop",
    description: "Django specialist with deep understanding of Python web development. Contributed to Django core and maintains several popular Django packages.",
  },
  {
    id: 11,
    name: "Robert Kim",
    role: "SEO Specialist",
    category: "fullstack",
    company: "Moz",
    designation: "SEO Strategy Lead",
    experience: "12+ years",
    image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop",
    description: "SEO expert with proven track record in improving search rankings and organic traffic. Regular speaker at SEO conferences and industry events.",
  },
  {
    id: 12,
    name: "Sophie Williams",
    role: "Google Ads Specialist",
    category: "fullstack",
    company: "Google",
    designation: "Digital Advertising Manager",
    experience: "8+ years",
    image: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop",
    description: "Google Ads expert with extensive experience in PPC campaigns and digital advertising. Google certified trainer for AdWords and Analytics.",
  }
];

export const courses = {
  1: {
    id: 1,
    title: "AI/ML",
    category: "aiml",
    description: "Comprehensive AI/ML training program with hands-on projects and placement assistance",
    metaTitle: "AI/ML Course | NxGen Tech Academy",
    metaDescription: "Master AI/ML with hands-on training, real-time projects, and 100% placement support",
    image: "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1200&h=600&fit=crop",
    duration: "45 Days",
    students: "200+ Students",
    rating: "4.9",
    price: "₹30,000",
    color: "from-red-600 to-red-500",
    icon: Brain,
    features: {
      duration: "45 Days Comprehensive Training Program",
      projects: "Work on 2 Real-Time Industry Projects",
      certification: "Course Completion Certificates Provided",
      placement: "100% Placement Assistance",
      skillDevelopment: "Hands-on Training with Practical Implementation",
      mentorship: "Guided by Experienced Industry Professionals",
      careerSupport: "Resume Building, Mock Interviews & Job Referrals"
    }
  },
  2: {
    id: 2,
    title: "PYTHON & AI/ML",
    category: "aiml",
    description: "Combined Python and AI/ML program with comprehensive training",
    metaTitle: "Python & AI/ML Course | NxGen Tech Academy",
    metaDescription: "Master Python and AI/ML with hands-on training and placement support",
    image: "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=1200&h=600&fit=crop",
    duration: "45 Days",
    students: "180+ Students",
    rating: "4.8",
    price: "₹50,000",
    color: "from-yellow-500 to-yellow-400",
    icon: Brain,
    features: {
      duration: "45 Days Comprehensive Training Program",
      projects: "Work on 2 Real-Time Industry Projects",
      certification: "Course Completion Certificates Provided",
      placement: "100% Placement Assistance",
      skillDevelopment: "Hands-on Training with Practical Implementation",
      mentorship: "Guided by Experienced Industry Professionals",
      careerSupport: "Resume Building, Mock Interviews & Job Referrals"
    }
  },
  3: {
    id: 3,
    title: "AI/ML & INTERNSHIP",
    category: "aiml",
    description: "Advanced AI/ML program with internship opportunity",
    metaTitle: "AI/ML with Internship | NxGen Tech Academy",
    metaDescription: "Get certified in AI/ML with internship experience and placement support",
    image: "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1200&h=600&fit=crop",
    duration: "45 Days",
    students: "150+ Students",
    rating: "4.9",
    price: "₹75,000",
    color: "from-green-600 to-green-500",
    icon: Brain,
    features: {
      duration: "45 Days Comprehensive Training Program",
      projects: "Work on 2 Real-Time Industry Projects",
      certification: "Internship & Course Completion Certificates Provided",
      placement: "100% Placement Assistance",
      skillDevelopment: "Hands-on Training with Practical Implementation",
      mentorship: "Guided by Experienced Industry Professionals",
      careerSupport: "Resume Building, Mock Interviews & Job Referrals"
    }
  },
  4: {
    id: 4,
    title: "PYTHON, AI/ML & INTERNSHIP",
    category: "aiml",
    description: "Complete package with Python, AI/ML training and internship",
    metaTitle: "Python, AI/ML & Internship | NxGen Tech Academy",
    metaDescription: "Complete Python and AI/ML program with internship and placement support",
    image: "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=1200&h=600&fit=crop",
    duration: "45 Days",
    students: "120+ Students",
    rating: "4.9",
    price: "₹100,000",
    color: "from-blue-600 to-blue-500",
    icon: Brain,
    features: {
      duration: "45 Days Comprehensive Training Program",
      projects: "Work on 2 Real-Time Industry Projects",
      certification: "Internship & Course Completion Certificates Provided",
      placement: "100% Placement Assistance",
      skillDevelopment: "Hands-on Training with Practical Implementation",
      mentorship: "Guided by Experienced Industry Professionals",
      careerSupport: "Resume Building, Mock Interviews & Job Referrals"
    }
  }
} as const satisfies Record<number, Course>;

// Helper functions
export const getCoursesByCategory = (category: string) => {
  if (category === "all") return Object.values(courses);
  return Object.values(courses).filter((course) => course.category === category);
};

export const getPreviewCourses = () => {
  return Object.values(courses);
};