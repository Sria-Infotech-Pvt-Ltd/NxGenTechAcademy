
export interface CourseData {
    id: string;
    title: string;
    description?: string;
    categoryId: string;
    image: string; // "code-icon" or URL
    rating: number;
    price: string;
    duration?: string;
    enrolled?: string;
    mode?: string;
}

export const categoryConfig: Record<string, { title: string; description: string; parentCategory: string; outcomes: string[] }> = {
    "sap-technical": {
        title: "SAP Technical & Development",
        description: "Master ABAP & core development skills for SAP ecosystems.",
        parentCategory: "SAP Courses",
        outcomes: [
            "Master ABAP programming language fundamentals and advanced concepts",
            "Develop custom reports, interfaces, conversions, and enhancements (RICE)",
            "Understand the SAP system landscape and architecture",
            "Gain proficiency in debugging and performance tuning of ABAP code",
            "Learn to build modern SAP applications using ABAP on HANA"
        ]
    },

    "sap-functional": {
        title: "SAP Functional Modules",
        description: "Optimize business processes efficiently with SAP Functional training.",
        parentCategory: "SAP Courses",
        outcomes: [
            "Understand end-to-end business processes in SAP (e.g., Order to Cash, Procure to Pay)",
            "Configure SAP modules (SD, MM, FICO, etc.) to meet business requirements",
            "Integrate different functional modules for seamless data flow",
            "Generate and analyze standard SAP reports for decision making",
            "Gain hands-on experience with real-world functional scenarios"
        ]
    },
    "python": {
        title: "Python Programming",
        description: "Learn comprehensive Python coding from basics to advanced.",
        parentCategory: "Python",
        outcomes: [
            "Master core Python syntax, data types, and control structures",
            "Apply Object-Readiness Programming (OOP) principles in Python",
            "Work with Python libraries and frameworks for various applications",
            "Handle file I/O, exceptions, and database connectivity",
            "Build real-world applications and scripts using Python"
        ]
    },
    "ai": {
        title: "AI Programing",
        description: "Learn Artificial intelligence training in Hyderabad with hands-on projects and expert trainers.",
        parentCategory: "AI",
        outcomes: [
            "Improves analytical thinking and logical reasoning",
            "Builds strong understanding of AI technologies",
            "Provides practical, project-based learning experience",
            "Enhances decision-making and prediction skills",
            "Develops real-world problem-solving abilities"
        ]
    },
    "aiml": {
        title: "AIML Programing",
        description: "AI and Machine Learning training in Hyderabad helps learners understand how systems learn from data and make accurate predictions.",
        parentCategory: "AIML",
        outcomes: [
            "Strengthens data analysis and interpretation skills",
            "Improves predictive modelling knowledge",
            "Provides real-time project experience",
            "Builds strong AIML fundamentals",
            "Enhances decision-making abilities"
        ]
    },
    "sap-btp": {
        title: "SAP Business Technology Platform (BTP)",
        description: "Build, extend, and integrate applications with SAP's unified cloud platform.",
        parentCategory: "SAP Courses",
        outcomes: [
            "Understand the SAP BTP architecture and its key pillars",
            "Develop and extend SAP applications using Low-Code/No-Code and Pro-Code tools",
            "Integrate SAP and non-SAP systems using SAP Integration Suite",
            "Leverage data and analytics capabilities with SAP HANA Cloud and SAC",
            "Implement security, DevOps, and automation on the platform"
        ]
    },
    /* Commented out per request - Mobile App Development category
    "mobile-app": {
        title: "Mobile App Development",
        description: "Build native and cross-platform mobile applications for iOS and Android.",
        parentCategory: "Mobile App Development",
        outcomes: [
            "Master mobile app development fundamentals and design patterns",
            "Develop native iOS applications using Swift and SwiftUI",
            "Develop native Android applications using Kotlin",
            "Build cross-platform apps using Flutter and React Native",
            "Implement mobile security, APIs, and real-time features",
            "Deploy and publish apps to App Store and Google Play Store"
        ]
    },
    */
    /* Commented out per request - Digital Marketing category
    "digital-marketing": {
        title: "Digital Marketing",
        description: "Master online marketing strategies to grow brands and drive business results.",
        parentCategory: "Digital Marketing",
        outcomes: [
            "Develop comprehensive digital marketing strategies for businesses",
            "Master SEO techniques to improve organic search rankings",
            "Create and manage effective social media marketing campaigns",
            "Design content marketing strategies that engage and convert",
            "Execute successful PPC and paid advertising campaigns",
            "Analyze marketing data to optimize campaign performance"
        ]
    },
    */
    /* Commented out per request - Data Analytics category
    "data-analytics": {
        title: "Data Analytics programing",
        description: "Master Data Analytics with Excel, SQL, Python, Power BI, and Tableau.",
        parentCategory: "Data Analytics",
        outcomes: [
            "Understand data collection and cleaning",
            "Learn data visualisation techniques",
            "Work with real-time datasets",
            "Build analytical dashboards"
        ]
    },
    */
};

export const coursesData: CourseData[] = [
    {
        id: "sap-abap-course-training",
        title: "SAP ABAP on HANA",
        description: "Modern ABAP development with reports, enhancements, performance tuning, and S/4HANA best practices.",
        categoryId: "sap-technical",
        image: "/sap/sap-abap.jpeg",
        rating: 5,
        price: "₹30,000"
    },
    {
        id: "sap-abap-cds-course-training",
        title: "SAP ABAP on HANA (CDS & OData Training)",
        description: "Advanced upskilling in CDS Views, OData services, and SAP HANA optimized development for S/4HANA.",
        categoryId: "sap-technical",
        image: "/sap/sap-abap-cds.jpg",
        rating: 5,
        price: "₹35,000"
    },
    {
        id: "sap-fiori-course-training",
        title: "SAP Fiori & UI5",
        description: "Front-end SAP application development using Fiori architecture, UI5, MVC, and OData integration.",
        categoryId: "sap-technical",
        image: "/sap/sap-fiori.jpg",
        rating: 5,
        price: "₹35,000"
    },
    // SAP Functional - UPDATED CONTENT
    {
        id: "sap-sd-course-training",
        title: "SAP SD (Sales & Distribution)",
        description: "Sales order processing, pricing, delivery, billing, and SD–MM–FICO integration.",
        categoryId: "sap-functional",
        image: "/sap/sap-sd.jpg",
        rating: 5,
        price: "₹28,000",
        duration: "10-12 weeks",
        enrolled: "1284+",
        mode: "Online / Offline"
    },
    {
        id: "sap-mm-course-training",
        title: "SAP MM (Materials Management)",
        description: "Procurement, inventory management, vendor handling, and invoice verification.",
        categoryId: "sap-functional",
        image: "/sap/sap-mm.jpg",
        rating: 5,
        price: "₹28,000",
        duration: "40+ hours",
        enrolled: "1452+",
        mode: "Online / Offline"
    },
    {
        id: "sap-fico-course-training",
        title: "SAP FICO (Financial Accounting & Controlling)",
        description: "Financial accounting, cost control, asset accounting, and reporting.",
        categoryId: "sap-functional",
        image: "/sap/sap-fico.jpg",
        rating: 5,
        price: "₹30,000",
        duration: "40+ hours",
        enrolled: "1584+",
        mode: "Online / Offline"
    },
    {
        id: "sap-pp-course-training",
        title: "SAP PP (Production Planning)",
        description: "BOM, routing, MRP, production orders, and capacity planning.",
        categoryId: "sap-functional",
        image: "/sap/sap-pp.jpg",
        rating: 5,
        price: "₹30,000",
        duration: "40+ hours",
        enrolled: "1230+",
        mode: "Online / Offline"
    },

    {
        id: "sap-qm-course-training",
        title: "SAP QM (Quality Management)",
        description: "Quality planning, inspections, notifications, and compliance management.",
        categoryId: "sap-functional",
        image: "/sap/sap-qm.jpg",
        rating: 5,
        price: "₹28,000"
    },

    {
        id: "sap-basis-course-training",
        title: "SAP BASIS S/4HANA Training",
        description: "SAP system administration, monitoring, transports, authorizations, and S/4HANA technical management.",
        categoryId: "sap-technical",
        image: "/sap/sap-basis.jpg",
        rating: 5,
        price: "₹30,000",
        duration: "40+ Hours",
        enrolled: "1100+",
        mode: "Online / Offline"
    },

    // SAP BTP - Courses
    {
        id: "sap-btp-professionals-course-training",
        title: "SAP BTP For Working Professionals",
        description: "Comprehensive SAP BTP module tailored for experienced working professionals.",
        categoryId: "sap-btp",
        image: "/sap/sap-btp-working.jpg",
        rating: 5,
        price: "₹40,000"
    },
    {
        id: "sap-btp-freshers-course-training",
        title: "SAP BTP For Freshers",
        description: "Foundational SAP BTP training designed specifically for freshers.",
        categoryId: "sap-btp",
        image: "/sap/sap-btp-freshers.jpg",
        rating: 5,
        price: "₹30,000"
    },
    {
        id: "sap-cpi-course-training",
        title: "SAP CPI Training",
        description: "Master SAP Cloud Integration (CPI), iFlows, adapters, and security within the SAP BTP ecosystem.",
        categoryId: "sap-btp",
        image: "/sap/sap-btp-cpi.jpg",
        rating: 5,
        price: "₹35,000"
    },

    // Python - Programming
    {
        id: "python-course-training",
        title: "Python Programming",
        description: "Python Course training focuses on practical learning and industry skills from scratch.",
        categoryId: "python",
        image: "/sap/python.png",
        rating: 5,
        price: "Contact Us",
        duration: "3 to 4 Months",
        enrolled: "1250+",
        mode: " Online / Offline"
    },

    // AI - UPDATED CONTENT
    {
        id: "ai-course-training",
        title: "AI Programing",
        description: "Artificial intelligence training in Hyderabad helps learners understand how machines think, learn, and act intelligently.",
        categoryId: "ai",
        image: "/AI/AI.png",
        rating: 5,
        price: "Contact Us",
        duration: "3 to 4 Months",
        enrolled: "1280+",
        mode: "Online / Offline"
    },

    // AIML - UPDATED CONTENT
    {
        id: "aiml-course-training",
        title: "AIML Programing",
        description: "AI and Machine Learning training in Hyderabad helps learners understand how systems learn from data and make accurate predictions.",
        categoryId: "aiml",
        image: "/AIML/AIML.png",
        rating: 5,
        price: "Contact Us",
        duration: "3 to 4 Months",
        enrolled: "1150+",
        mode: "Online / Offline"
    },

    /* Commented out per request - Mobile App Development courses
    // Mobile App Development - Courses
    {
        id: "ios-app-development-course-training",
        title: "iOS App Development (Swift)",
        description: "Master native iOS app development using Swift and SwiftUI with hands-on projects.",
        categoryId: "mobile-app",
        image: "/mobile/ios-development.jpg",
        rating: 5,
        price: "Contact Us",
        duration: "3 to 4 Months",
        enrolled: "0+",
        mode: "Online / Offline"
    },
    {
        id: "android-app-development-course-training",
        title: "Android App Development (Kotlin)",
        description: "Develop native Android applications using Kotlin with modern development practices.",
        categoryId: "mobile-app",
        image: "/mobile/android-development.jpg",
        rating: 5,
        price: "Contact Us",
        duration: "3 to 4 Months",
        enrolled: "0+",
        mode: "Online / Offline"
    },
    {
        id: "flutter-app-development-course-training",
        title: "Flutter Cross-Platform Development",
        description: "Build beautiful cross-platform mobile apps for iOS and Android using Flutter.",
        categoryId: "mobile-app",
        image: "/mobile/flutter-development.jpg",
        rating: 5,
        price: "Contact Us",
        duration: "3 to 4 Months",
        enrolled: "0+",
        mode: "Online / Offline"
    },
    {
        id: "react-native-app-development-course-training",
        title: "React Native App Development",
        description: "Create cross-platform mobile apps using React Native with JavaScript/TypeScript.",
        categoryId: "mobile-app",
        image: "/mobile/react-native-development.jpg",
        rating: 5,
        price: "Contact Us",
        duration: "3 to 4 Months",
        enrolled: "0+",
        mode: "Online / Offline"
    },
    */

    /* Commented out per request - Digital Marketing courses
    // Digital Marketing Courses
    {
        id: "digital-marketing-job-guarantee-course-training",
        title: "Job Guarantee Digital Marketing Course",
        description: "6 months advanced training program in Hyderabad focusing on practical learning, AI tools, and 100% placement help.",
        categoryId: "digital-marketing",
        image: "/DM1.png",
        rating: 5,
        price: "Contact Us",
        duration: "6 Months",
        enrolled: "850+",
        mode: "Online / Offline"
    },
    {
        id: "digital-marketing-course-training",
        title: "Digital Marketing Course",
        description: "3 months fast-track training program in Hyderabad covering essential SEO, PPC, and Social Media Marketing skills.",
        categoryId: "digital-marketing",
        image: "/DM2.png",
        rating: 5,
        price: "Contact Us",
        duration: "3 Months",
        enrolled: "1200+",
        mode: "Online / Offline"
    },
    */
    /* Commented out per request - Data Analytics course
    {
        id: "data-analytics-course-training",
        title: "Data Analytics programing",
        description: "Data analytics online training helps you gain in-demand skills and build a successful career.",
        categoryId: "data-analytics",
        image: "/data-analytics.jpg",
        rating: 5,
        price: "Contact Us",
        duration: "3 to 4 Months",
        enrolled: "1500+",
        mode: "Online / Offline"
    }
    */
];
