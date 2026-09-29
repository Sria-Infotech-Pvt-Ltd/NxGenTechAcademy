import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Suspense, lazy, useEffect } from "react";
import { BrowserRouter, Routes, Route, useLocation, Navigate } from "react-router-dom";
import GTMPageView from "./GTMPageView";
import { Helmet } from 'react-helmet-async';
import { Preloader } from "./components/Preloader";
import { Navbar } from "./components/Navbar";
import { Footer } from "./components/Footer";
import { ScrollToTop } from "./components/ScrollToTop";
import { TopBar } from "./components/TopBar"; // New Import
import { WhatsAppButton } from "./components/WhatsAppButton";
// Home stays eagerly bundled - it's the landing page for most visitors,
// so lazy-loading it would add a network round trip to the LCP path.
import Home from "./pages/Home";
import { categories } from './data';
import ProtectedRoute from "./components/ProtectedRoute";

// Every other route is code-split so its JS/CSS is only fetched when
// that route is actually visited (admin/instructor/student dashboards,
// auth pages, finance pages, etc. were previously all bundled into the
// homepage's initial load).
const About = lazy(() => import("./pages/About"));
const Courses = lazy(() => import("./pages/Courses"));
const CategoryListing = lazy(() => import("./pages/CategoryListing"));
const CourseDetail = lazy(() => import("./pages/CourseDetail"));
const ContactPage = lazy(() => import("./pages/ContactPage"));
const NotFound = lazy(() => import("./pages/NotFound"));
const WhyChooseUs = lazy(() => import("./pages/WhyChooseUs"));
const Partners = lazy(() => import("./pages/Partners"));
const Mentors = lazy(() => import("./pages/Mentors"));

const AllCourses = lazy(() => import("./pages/AllCourses"));
const Blogs = lazy(() => import("./pages/Blogs"));
const SAPCategory = lazy(() => import("./pages/SAPCategory"));
const Register = lazy(() => import("./pages/Auth/Register"));
const Login = lazy(() => import("./pages/Auth/Login"));
const ForgotPassword = lazy(() => import("./pages/Auth/ForgotPassword"));
const ChangePassword = lazy(() => import("./pages/Auth/ChangePassword"));
const MainDashboard = lazy(() => import("./pages/Admin/MainDashboard"));
const StudentsPage = lazy(() => import("./pages/Admin/StudentsPage"));
const StudentDetailPage = lazy(() => import("./pages/Admin/StudentDetailPage"));
const InstructorsPage = lazy(() => import("./pages/Admin/InstructorsPage"));
const AddInstructor = lazy(() => import("./pages/Admin/AddInstructor"));
const InstructorDashboard = lazy(() => import("./pages/Instructor/InstructorDashboard"));
const InstructorProfile = lazy(() => import("./pages/Instructor/InstructorProfile"));
const InstructorCourses = lazy(() => import("./pages/Instructor/InstructorCourses"));
const InstructorLessons = lazy(() => import("./pages/Instructor/InstructorLessons"));
const InstructorModuleLessons = lazy(() => import("./pages/Instructor/InstructorModuleLessons"));
const InstructorStudents = lazy(() => import("./pages/Instructor/InstructorStudents"));
const InstructorAssignments = lazy(() => import("./pages/Instructor/InstructorAssignments"));
const AdminBatches = lazy(() => import("./pages/Admin/AdminBatches"));
const AdminCourses = lazy(() => import("./pages/Admin/AdminCourses"));
const AdminAssignments = lazy(() => import("./pages/Admin/AdminAssignments"));
const Presales = lazy(() => import("./pages/Admin/Presales"));
const InstructorTopics = lazy(() => import("./pages/Instructor/InstructorTopics"));
const StudentDashboard = lazy(() => import("./pages/Student/StudentDashboard"));
const StudentCourses = lazy(() => import("./pages/Student/StudentCourses"));
const StudentAssignments = lazy(() => import("./pages/Student/StudentAssignments"));
const StudentProgress = lazy(() => import("./pages/Student/StudentProgress"));
const StudentCertificates = lazy(() => import("./pages/Student/StudentCertificates"));
const StudentProfile = lazy(() => import("./pages/Student/StudentProfile"));
const BlogDashboard = lazy(() => import("./pages/BlogAdmin/BlogDashboard"));
const CourseViewer = lazy(() => import("./pages/Dashboard/CourseViewer"));
const BlogDetail = lazy(() => import("./pages/BlogDetail"));
const PrivacyPolicy = lazy(() => import("./pages/PrivacyPolicy"));
const Payments = lazy(() => import("@/pages/Payments"));
const StudentPaymentHistory = lazy(() => import("./pages/Student/StudentPaymentHistory"));
const StudentInvoices = lazy(() => import("./pages/Student/StudentInvoices"));
const StudentInvoiceDetail = lazy(() => import("./pages/Student/StudentInvoiceDetail"));
const Transactions = lazy(() => import("./pages/Admin/Finance/Transactions"));
const Invoices = lazy(() => import("./pages/Admin/Finance/Invoices"));
const AdminInvoiceDetail = lazy(() => import("./pages/Admin/Finance/AdminInvoiceDetail"));
const Refunds = lazy(() => import("./pages/Admin/Finance/Refunds"));
const Reports = lazy(() => import("./pages/Admin/Finance/Reports"));

const RouteFallback = () => (
  <div className="flex items-center justify-center min-h-[40vh]">
    <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" />
  </div>
);

const queryClient = new QueryClient();

const AppContent = () => {
  const location = useLocation();
  const authPages = ["/register", "/login", "/forgot-password", "/student-login", "/instructor-login", "/admin-login"];
  const isAuthPage = authPages.includes(location.pathname);

  const role = localStorage.getItem("role");
  const isDashboardPage = location.pathname.startsWith("/admin") ||
    location.pathname.startsWith("/instructor") ||
    location.pathname.startsWith("/student") ||
    location.pathname.startsWith("/blog-admin") ||
    location.pathname.startsWith("/payments");

  const token = localStorage.getItem("access_token");
  const isUserLoggedIn = !!token;

  // Hide TopBar, Navbar, and Footer for auth pages and all dashboard routes.
  const hideComponents = isAuthPage || isDashboardPage;

  return (
    <>
      <GTMPageView />
      <ScrollToTop />
      {!hideComponents && <TopBar />}
      {!hideComponents && <Navbar />}
      <main>
        <Suspense fallback={<RouteFallback />}>
        <Routes>
          <Route index element={<Home />} />
          <Route path="about-us" element={<About />} />
          <Route path="courses" element={<Courses />} />
          <Route path="/training-programs" element={<AllCourses />} />
          <Route path="courses-menu" element={<AllCourses />} />
          <Route path="courses/sap-courses" element={<SAPCategory />} />
          <Route path="courses/sap-technical" element={<CategoryListing categorySlug="sap-technical" />} />
          <Route path="courses/sap-functional" element={<CategoryListing categorySlug="sap-functional" />} />
          <Route path="courses/python" element={<CategoryListing categorySlug="python" />} />
          <Route path="courses/ai" element={<CategoryListing categorySlug="ai" />} />
          <Route path="courses/aiml" element={<CategoryListing categorySlug="aiml" />} />
          {/* Commented out per request - Data Analytics category route
          <Route path="courses/data-analytics" element={<CategoryListing categorySlug="data-analytics" />} />
          */}
          {/* Commented out per request - Digital Marketing category route
          <Route path="courses/digital-marketing" element={<CategoryListing categorySlug="digital-marketing" />} />
          */}
          <Route path="courses/sap-btp" element={<CategoryListing categorySlug="sap-btp" />} />
          {/* Commented out per request - Mobile App Development category route
          <Route path="courses/mobile-app" element={<CategoryListing categorySlug="mobile-app" />} />
          */}
          <Route path="courses/:id" element={<CourseDetail />} />

          {/* Old slugs kept as redirects so existing links/bookmarks/SEO don't break */}
          <Route path="about" element={<Navigate to="/about-us" replace />} />
          <Route path="contact" element={<Navigate to="/contact-us" replace />} />
          <Route path="/all-courses" element={<Navigate to="/training-programs" replace />} />
          <Route path="/sap-courses" element={<Navigate to="/courses/sap-courses" replace />} />
          <Route path="courses/sap-abap-on-hana-course-online" element={<Navigate to="/courses/sap-abap-course-training" replace />} />
          <Route path="courses/sap-abap-rap" element={<Navigate to="/courses/sap-abap-cds-course-training" replace />} />
          <Route path="courses/sap-ui5-fiori-training" element={<Navigate to="/courses/sap-fiori-course-training" replace />} />
          <Route path="courses/sap-mm-course" element={<Navigate to="/courses/sap-mm-course-training" replace />} />
          <Route path="courses/sap-pp-course" element={<Navigate to="/courses/sap-pp-course-training" replace />} />
          <Route path="courses/sap-qm-course" element={<Navigate to="/courses/sap-qm-course-training" replace />} />
          <Route path="courses/sap-basis-s4hana-training" element={<Navigate to="/courses/sap-basis-course-training" replace />} />
          <Route path="courses/sap-btp-working-professionals" element={<Navigate to="/courses/sap-btp-professionals-course-training" replace />} />
          <Route path="courses/sap-btp-freshers" element={<Navigate to="/courses/sap-btp-freshers-course-training" replace />} />
          <Route path="courses/sap-cpi-training" element={<Navigate to="/courses/sap-cpi-course-training" replace />} />
          <Route path="courses/python-course-training-hyderabad" element={<Navigate to="/courses/python-course-training" replace />} />
          <Route path="courses/artificial-intelligence-training-hyderabad" element={<Navigate to="/courses/ai-course-training" replace />} />
          <Route path="courses/aiml-training-hyderabad" element={<Navigate to="/courses/aiml-course-training" replace />} />
          {/* Commented out per request - Digital Marketing redirects
          <Route path="courses/job-guarantee-digital-marketing-course" element={<Navigate to="/courses/digital-marketing-job-guarantee-course-training" replace />} />
          <Route path="courses/digital-marketing-course-hyderabad" element={<Navigate to="/courses/digital-marketing-course-training" replace />} />
          */}
          {/* Commented out per request - Data Analytics redirect
          <Route path="courses/data-analytics-online-training" element={<Navigate to="/courses/data-analytics-course-training" replace />} />
          */}
          <Route path="mentors" element={<Mentors />} />
          <Route path="contact-us" element={<ContactPage />} />
          <Route path="why-choose-us" element={<WhyChooseUs />} />
          <Route path="bsnl-skill-development-partner" element={<Partners />} />
          <Route path="blogs" element={<Blogs />} />
          <Route path="blogs/:slug" element={<BlogDetail />} />
          <Route path="register" element={<Register />} />
          <Route path="login" element={<Login />} />
          <Route path="forgot-password" element={<ForgotPassword />} />

          {/* Legacy Login Routes (Redirecting to new login) */}
          <Route path="student-login" element={<Login />} />
          <Route path="instructor-login" element={<Login />} />
          <Route path="admin-login" element={<Login />} />

          {/* Protected Dashboard Routes */}
          <Route path="admin/*" element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <Routes>
                <Route path="/" element={<MainDashboard />} />
                <Route path="Presales" element={<Presales />} />
                <Route path="dashboard" element={<MainDashboard />} />
                <Route path="students" element={<StudentsPage />} />
                <Route path="students/:id" element={<StudentDetailPage />} />
                <Route path="instructors" element={<InstructorsPage />} />
                <Route path="instructors/add" element={<AddInstructor />} />
                <Route path="courses" element={<AdminCourses />} />
                <Route path="batches" element={<AdminBatches />} />
                <Route path="assignments" element={<AdminAssignments />} />
                <Route path="finance/transactions" element={<Transactions />} />
                <Route path="finance/invoices" element={<Invoices />} />
                <Route path="finance/invoices/:enrollmentId" element={<AdminInvoiceDetail />} />
                <Route path="finance/refunds" element={<Refunds />} />
                <Route path="finance/reports" element={<Reports />} />
              </Routes>
            </ProtectedRoute>
          } />

          <Route path="instructor/*" element={
            <ProtectedRoute allowedRoles={["instructor"]}>
              <Routes>
                <Route path="/" element={<InstructorDashboard />} />
                <Route path="dashboard" element={<InstructorDashboard />} />
                <Route path="courses" element={<InstructorCourses />} />
                <Route path="courses/:courseId/lessons" element={<InstructorLessons />} />
                <Route path="courses/:courseId/modules/:moduleId/lessons" element={<InstructorModuleLessons />} />
                <Route path="lessons/:lessonId/topics" element={<InstructorTopics />} />
                <Route path="students" element={<InstructorStudents />} />
                <Route path="assignments" element={<InstructorAssignments />} />
                <Route path="profile" element={<InstructorProfile />} />
                <Route path="change-password" element={<ChangePassword />} />
              </Routes>
            </ProtectedRoute>
          } />

          <Route path="student/*" element={
            <ProtectedRoute allowedRoles={["student"]}>
              <Routes>
                <Route path="/" element={<StudentDashboard />} />
                <Route path="dashboard" element={<StudentDashboard />} />
                <Route path="change-password" element={<ChangePassword />} />
                <Route path="courses" element={<StudentCourses />} />
                <Route path="assignments" element={<StudentAssignments />} />
                <Route path="progress" element={<StudentProgress />} />
                <Route path="certificates" element={<StudentCertificates />} />
                <Route path="profile" element={<StudentProfile />} />
                <Route path="course/:id" element={<CourseViewer />} />
                <Route path="payment-history" element={<StudentPaymentHistory />} />
                <Route path="invoices" element={<StudentInvoices />} />
                <Route path="invoices/:enrollmentId" element={<StudentInvoiceDetail />} />
              </Routes>
            </ProtectedRoute>
          } />

          <Route path="payments" element={
            <ProtectedRoute allowedRoles={["student"]}>
              <Payments />
            </ProtectedRoute>
          } />

          <Route path="blog-admin/*" element={
            <ProtectedRoute allowedRoles={["blog_admin"]}>
              <BlogDashboard />
            </ProtectedRoute>
          } />

          <Route path="privacy-policy" element={<PrivacyPolicy />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
        </Suspense>
      </main>
      {!hideComponents && <Footer />}
      {/* Shown on every page - before login, after login, and on every dashboard */}
      <WhatsAppButton />
    </>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <div className="min-h-screen text-black bg-white">
        <Helmet>
          <title>NxGen Tech Academy - Best IT Training & Placement Institute in Hyderabad</title>
          <meta name="description" content="Join Our 100% Job Guarantee Courses. NxGen Tech Academy offers best IT training in Hyderabad." />
          <meta name="keywords" content={categories.map(c => c.name).join(', ')} />
        </Helmet>

        <Toaster />
        <Sonner />
        <Preloader />
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </div>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
