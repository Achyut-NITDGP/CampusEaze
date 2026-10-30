import { ReactElement } from "react";
import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import Navbar from "./components/common/Navbar";
import Sidebar from "./components/common/Sidebar";
import { useAuth } from "./contexts/AuthContext";
import AdminDashboard from "./pages/AdminDashboard";
import BookingDetails from "./pages/BookingDetails";
import CheckInOut from "./pages/CheckInOut";
import Checkout from "./pages/Checkout";
import CreateResource from "./pages/CreateResource";
import Home from "./pages/Home";
import Incidents from "./pages/Incidents";
import Login from "./pages/Login";
import MyBookings from "./pages/MyBookings";
import Notifications from "./pages/Notifications";
import Profile from "./pages/Profile";
import Register from "./pages/Register";
import ResourceDetails from "./pages/ResourceDetails";
import ResourceSearch from "./pages/ResourceSearch";
import AdminNotifications from "./pages/admin/AdminNotifications";
import AssetInventory from "./pages/admin/AssetInventory";
import AuditLogs from "./pages/admin/AuditLogs";
import BookingRequests from "./pages/admin/BookingRequests";
import HandoverReview from "./pages/admin/HandoverReview";
import IncidentCentre from "./pages/admin/IncidentCentre";
import ResourceManagement from "./pages/admin/ResourceManagement";
import Transactions from "./pages/admin/Transactions";
import UsersVerification from "./pages/admin/UsersVerification";

const STAFF = ["owner", "manager", "admin"];
const ADMINS = ["manager", "admin"];

function Guard({ roles, children }: { roles?: string[]; children: ReactElement }) {
  const { user, loading } = useAuth();
  if (loading) return <p aria-busy="true">Loading…</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;
  return children;
}

function Shell({ admin }: { admin?: boolean }) {
  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <Navbar />
      <div className={admin ? "with-side" : ""}>
        {admin && <Sidebar />}
        <main id="main" tabIndex={-1}><Outlet /></main>
      </div>
    </>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route element={<Guard><Shell /></Guard>}>
        <Route path="/" element={<Home />} />
        <Route path="/resources" element={<ResourceSearch />} />
        <Route path="/resources/:id" element={<ResourceDetails />} />
        <Route path="/resources/:id/book" element={<Checkout />} />
        <Route path="/bookings" element={<MyBookings />} />
        <Route path="/bookings/:id" element={<BookingDetails />} />
        <Route path="/bookings/:id/handover" element={<CheckInOut />} />
        <Route path="/incidents" element={<Incidents />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/profile" element={<Profile />} />
      </Route>
      <Route path="/admin" element={<Guard roles={STAFF}><Shell admin /></Guard>}>
        <Route index element={<AdminDashboard />} />
        <Route path="requests" element={<BookingRequests />} />
        <Route path="handover" element={<HandoverReview />} />
        <Route path="inventory" element={<AssetInventory />} />
        <Route path="resources" element={<ResourceManagement />} />
        <Route path="resources/new" element={<CreateResource />} />
        <Route path="resources/:id/edit" element={<CreateResource />} />
        <Route path="incidents" element={<IncidentCentre />} />
        <Route path="users" element={<Guard roles={ADMINS}><UsersVerification /></Guard>} />
        <Route path="transactions" element={<Guard roles={ADMINS}><Transactions /></Guard>} />
        <Route path="audit" element={<Guard roles={ADMINS}><AuditLogs /></Guard>} />
        <Route path="notifications" element={<Guard roles={ADMINS}><AdminNotifications /></Guard>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
