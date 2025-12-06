import React from "react";
import { useAuth } from "../context/AuthContext";

export function LogoutButton() {
    const { signOut } = useAuth();

    return <button onClick={signOut}>Logout</button>;
}

