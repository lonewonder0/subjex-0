"use client";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function HomePage() {
  const [isLoggedIn, setIsLoggedIn] = useState({ state: false, pending: false });
  const [isAdmin, setIsAdmin] = useState<boolean>(false);

  useEffect(() => {
    async function GetSession() {
      setIsLoggedIn((prev) => {
        return { ...prev, pending: true };
      });

      const res = await fetch(`${window.location.origin}/api/session`, {
        method: "GET",
        cache: "no-cache",
        credentials: "include",
      });

      if (res.status == 200) {
        setIsLoggedIn(() => {
          return { state: true, pending: false };
        });
        const { role }: { role: string } = await res.json();

        if (role == "admin") {
          setIsAdmin(() => {
            return true;
          });
        }
      } else {
        setIsLoggedIn((prev) => {
          return { ...prev, pending: false };
        });
      }
    }
    GetSession();
  }, []);

  function LoggedIn({ isAdmin }: { isAdmin: boolean }) {
    return (
      <>
        <div className='flex flex-row gap-4'>
          <Link
            href={"/tickets"}
            className='flex px-4 py-2 rounded-sm shadow-md bg-blue-200 hover:bg-blue-400 hover:underline'
          >
            Check Your Tickets
          </Link>
          {isAdmin && (
            <Link
              href={"/createTicket"}
              className='flex px-4 py-2 rounded-sm shadow-md text-white bg-blue-600 hover:bg-blue-800 hover:underline'
            >
              Create Ticket (Admin)
            </Link>
          )}

          <button
            className='flex px-4 py-2 rounded-sm shadow-md text-white bg-gray-600 hover:bg-gray-800 hover:underline'
            onClick={() => {
              fetch(`${window.location.origin}/api/logout`, {
                method: "POST",
                cache: "no-cache",
                credentials: "include",
              });
              setIsLoggedIn((prev) => {
                return { ...prev, state: false };
              });
            }}
          >
            Logout
          </button>
        </div>
      </>
    );
  }

  function NotLoggedIn() {
    return (
      <div className='flex flex-row gap-4'>
        <Link
          href={"/login"}
          className='flex px-4 py-2 rounded-sm shadow-md bg-blue-200 hover:bg-blue-400 hover:underline'
        >
          Login
        </Link>
        <Link
          href={"/createAccount"}
          className='flex px-4 py-2 rounded-sm shadow-md text-white bg-blue-600 hover:bg-blue-800 hover:underline'
        >
          Create Account
        </Link>
      </div>
    );
  }

  return (
    <>
      {isLoggedIn.pending == false ? (
        <div className='flex flex-col gap-4 w-full h-full items-center justify-center'>
          <h1 className='flex text-5xl bold'>Subjex Ticket Manager</h1>
          {isLoggedIn.state == true ? <LoggedIn isAdmin={isAdmin} /> : <NotLoggedIn />}
        </div>
      ) : (
          <div></div>
      )}
    </>
  );
}
