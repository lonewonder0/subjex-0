"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function LoginPage() {
  const [message, setMessage] = useState<string>("");
  const router = useRouter();

  useEffect(() => {
    async function CheckIfAlreadyLoggedIn() {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/session`, {
        method: "GET",
        cache: "no-cache",
        credentials: "include",
      });
      if (res.status == 200) {
        router.replace("/");
      }
    }
    CheckIfAlreadyLoggedIn();
  }, [router]);

  function FormActionFunc(formData: FormData) {
    async function SendLogin() {
      if (formData == null) {
        return;
      }

      const username = formData.get("username")?.toString();
      const password = formData.get("password")?.toString();

      if (username == null || password == null) {
        return;
      }

      const body = {
        username: username,
        password: password,
      };

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/login`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (res.status == 200) {
        setMessage("Successfully logged in.");
        router.replace("/");
      } else if (res.status == 401) {
        setMessage("Unauthorised. Invalid Credentials.");
      } else {
        setMessage("Server Error.");
      }
    }

    SendLogin();
  }

  return (
    <div className='flex flex-col gap-4 w-full h-full items-center justify-center'>
      <h1 className='flex text-3xl'>Login</h1>
      <form
        action={FormActionFunc}
        className='flex flex-col gap-4 w-[50%] border-gray-200 border-[1px] shadow-md p-4 rounded-md'
      >
        <input
          type='text'
          id='username'
          name='username'
          required
          placeholder='Username'
          className='flex px-4 py-2 rounded-sm shadow-md bg-gray-100 border-[1px] border-gray-400'
        />
        <input
          type='password'
          id='password'
          name='password'
          required
          placeholder='Password'
          className='flex px-4 py-2 rounded-sm shadow-md bg-gray-100 border-[1px] border-gray-400'
        />
        <button
          type='submit'
          className='flex px-4 py-2 rounded-sm shadow-md bg-blue-200 hover:bg-blue-400 hover:underline text-center items-center justify-center'
        >
          Login
        </button>
        <p className='flex text-1xl italic'>{message}</p>
      </form>
    </div>
  );
}
