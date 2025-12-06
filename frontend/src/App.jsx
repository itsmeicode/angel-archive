import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "../context/AuthContext";
import { LandingPage } from "../pages/LandingPage";  
import SignUpPage from "../pages/SignupPage";  
import LoginPage from "../pages/LoginPage"; 
import { DashboardPage } from "../pages/DashboardPage";  
import { NavBarDashboard } from "../components/NavBarDashboard";  
import { NavBarLanding } from "../components/NavBarLanding";  
import { ProfilePage } from "../pages/ProfilePage";

function ProtectedRoute({ children }) {
    const { user } = useAuth();
    return user ? children : <Navigate to="/" />;
}

function AuthNav() {
    const { user } = useAuth();

    return (
        <div 
            style={{
                position: "sticky", 
                top: 0, 
                zIndex: 1000, 
                backgroundColor: "cyan", 
                boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)"
            }}
        >
            {user ? <NavBarDashboard /> : <NavBarLanding />}
        </div>
    );
}

function App() {
    return (
        <Router>
            <AuthProvider>  
                <AuthNav />  
                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/signup" element={<SignUpPage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
                    <Route path="/profile" element={<ProfilePage />} />
                </Routes>
            </AuthProvider>
        </Router>
    );
}

export default App;

