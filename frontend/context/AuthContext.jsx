import React, { createContext, useContext, useEffect, useState } from "react";
import supabase from "../config/supabaseClient";
import api from "../src/services/api";

const AuthContext = createContext();

export function useAuth() {
    return useContext(AuthContext);
}

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkUser = async () => {
            try {
                const data = await api.auth.getUser();
                setUser(data?.user || null);
            } catch (err) {
                setUser(null);
            } finally {
                setLoading(false);
            }
        };

        checkUser();

        const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
            setUser(session?.user || null);
        });

        return () => {
            listener?.subscription?.unsubscribe();
        };
    }, []);

    const signIn = async (identifier, password) => {
        let email = identifier;

        if (!identifier.includes("@")) {
            try {
                const data = await api.auth.getUserByUsername(identifier);
                email = data.email;
            } catch (err) {
                throw new Error("Username not found.");
            }
        }

        try {
            await api.auth.login({ email, password });
            const data = await api.auth.getUser();
            setUser(data?.user);
        } catch (err) {
            throw new Error("Incorrect email or password.");
        }
    };

    const signOut = async () => {
        if (user) {
            await api.auth.logout(user.id);
        }
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, signIn, signOut }}>
            {!loading && children}
        </AuthContext.Provider>
    );
}
