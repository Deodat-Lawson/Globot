import React, { createContext, useCallback, useContext, useMemo, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

const AUTH_STORAGE_KEY = "globot_mock_signed_in";

type MockUser = {
  id: string;
  fullName: string;
  firstName: string;
  username: string;
  imageUrl: string;
  primaryEmailAddress: { emailAddress: string };
  publicMetadata: { role: string };
};

type ClerkContextValue = {
  isSignedIn: boolean;
  user: MockUser | null;
  signIn: () => void;
  signOut: () => void;
};

const DEFAULT_USER: MockUser = {
  id: "mock_user_001",
  fullName: "Mock Admin",
  firstName: "Mock",
  username: "mock.admin",
  imageUrl: "https://api.dicebear.com/9.x/identicon/svg?seed=mock-admin",
  primaryEmailAddress: { emailAddress: "admin@example.com" },
  publicMetadata: { role: "admin" },
};

const ClerkContext = createContext<ClerkContextValue | null>(null);

function readAuthState(): boolean {
  if (typeof window === "undefined") return true;
  const saved = window.localStorage.getItem(AUTH_STORAGE_KEY);
  if (saved === null) {
    window.localStorage.setItem(AUTH_STORAGE_KEY, "true");
    return true;
  }
  return saved === "true";
}

function useClerkContext(): ClerkContextValue {
  const value = useContext(ClerkContext);
  if (!value) {
    throw new Error("Mock Clerk context missing. Wrap app with ClerkProvider.");
  }
  return value;
}

export function ClerkProvider({ children }: { children: React.ReactNode }) {
  const [isSignedIn, setIsSignedIn] = useState<boolean>(() => readAuthState());

  const signIn = useCallback(() => {
    setIsSignedIn(true);
    if (typeof window !== "undefined") {
      window.localStorage.setItem(AUTH_STORAGE_KEY, "true");
    }
  }, []);

  const signOut = useCallback(() => {
    setIsSignedIn(false);
    if (typeof window !== "undefined") {
      window.localStorage.setItem(AUTH_STORAGE_KEY, "false");
    }
  }, []);

  const value = useMemo(
    () => ({
      isSignedIn,
      user: isSignedIn ? DEFAULT_USER : null,
      signIn,
      signOut,
    }),
    [isSignedIn, signIn, signOut]
  );

  return <ClerkContext.Provider value={value}>{children}</ClerkContext.Provider>;
}

export function SignedIn({ children }: { children: React.ReactNode }) {
  const { isSignedIn } = useClerkContext();
  return isSignedIn ? <>{children}</> : null;
}

export function SignedOut({ children }: { children: React.ReactNode }) {
  const { isSignedIn } = useClerkContext();
  return isSignedIn ? null : <>{children}</>;
}

export function RedirectToSignIn() {
  return <Navigate to="/sign-in" replace />;
}

export function useUser() {
  const { user, isSignedIn } = useClerkContext();
  return {
    isLoaded: true,
    isSignedIn,
    user,
  };
}

export function useAuth() {
  const { isSignedIn, signOut } = useClerkContext();
  return {
    isLoaded: true,
    isSignedIn,
    getToken: async () => (isSignedIn ? "mock-clerk-token" : null),
    signOut: async () => signOut(),
  };
}

export function useClerk() {
  const navigate = useNavigate();
  const { signOut } = useClerkContext();
  return {
    openSignIn: () => navigate("/sign-in"),
    openSignUp: () => navigate("/sign-up"),
    signOut: async () => signOut(),
  };
}

type AuthCardProps = {
  title: string;
  description: string;
  buttonLabel: string;
  redirectTo: string;
};

function AuthCard({ title, description, buttonLabel, redirectTo }: AuthCardProps) {
  const navigate = useNavigate();
  const { signIn } = useClerkContext();

  return (
    <div
      style={{
        width: 420,
        maxWidth: "92vw",
        background: "#111827",
        border: "1px solid #1f2937",
        borderRadius: 12,
        padding: 24,
        color: "white",
      }}
    >
      <h2 style={{ marginTop: 0 }}>{title}</h2>
      <p style={{ color: "#9ca3af", marginBottom: 18 }}>{description}</p>
      <button
        onClick={() => {
          signIn();
          navigate(redirectTo);
        }}
        style={{
          width: "100%",
          padding: "10px 14px",
          border: "none",
          borderRadius: 8,
          background: "#2563eb",
          color: "white",
          cursor: "pointer",
          fontWeight: 600,
        }}
      >
        {buttonLabel}
      </button>
    </div>
  );
}

export function SignIn(props: { afterSignInUrl?: string }) {
  return (
    <AuthCard
      title="Mock Sign In"
      description="This project is using a local mocked login instead of Clerk."
      buttonLabel="Continue as Mock User"
      redirectTo={props.afterSignInUrl || "/port"}
    />
  );
}

export function SignUp(props: { afterSignUpUrl?: string }) {
  return (
    <AuthCard
      title="Mock Sign Up"
      description="Sign-up is mocked. Continue to create a mock session."
      buttonLabel="Create Mock Account"
      redirectTo={props.afterSignUpUrl || "/port"}
    />
  );
}

export function SignOutButton({
  children,
  signOutCallback,
}: {
  children: React.ReactNode;
  signOutCallback?: () => void;
}) {
  const { signOut } = useClerkContext();
  const handleSignOut = () => {
    signOut();
    signOutCallback?.();
  };

  if (typeof children === "function") {
    return <>{(children as (args: { signOut: () => void }) => React.ReactNode)({ signOut: handleSignOut })}</>;
  }

  if (React.isValidElement(children)) {
    const existingOnClick = (children.props as { onClick?: (e: React.MouseEvent) => void }).onClick;
    return React.cloneElement(children, {
      onClick: (e: React.MouseEvent) => {
        existingOnClick?.(e);
        handleSignOut();
      },
    });
  }

  return <button onClick={handleSignOut}>Sign Out</button>;
}

export function UserButton({ afterSignOutUrl = "/pay" }: { afterSignOutUrl?: string }) {
  const { user, signOut } = useClerkContext();
  const navigate = useNavigate();

  return (
    <button
      onClick={() => {
        signOut();
        navigate(afterSignOutUrl);
      }}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        border: "1px solid #334155",
        borderRadius: 9999,
        padding: "6px 10px",
        background: "#1e293b",
        color: "white",
        cursor: "pointer",
      }}
      title="Mock Sign Out"
    >
      <img
        src={user?.imageUrl || ""}
        alt="avatar"
        style={{ width: 20, height: 20, borderRadius: "50%" }}
      />
      <span style={{ fontSize: 12 }}>Sign out</span>
    </button>
  );
}
