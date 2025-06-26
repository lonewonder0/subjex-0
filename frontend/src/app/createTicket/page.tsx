"use client";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function CreateTicket() {
  const router = useRouter();

  const [isLoggedIn, setIsLoggedIn] = useState({ state: false, pending: true });
  const [message, setMessage] = useState("");
  const [username, setUsername] = useState<string>("");
  const [users, setUsers] = useState<{ state: Array<{ user_id: number; username: string }>; pending: boolean }>({
    state: [],
    pending: true,
  });
  const [selectedUserIds, setSelectedUserIds] = useState<number[]>([]);

  useEffect(() => {
    async function GetSession() {
      // This stops the usage of data in the client roll out before it's been fetched.
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

        const { role, username }: { role: string; username: string } = await res.json();

        if (username != null) {
          setUsername(username);
        }

        if (role != "admin") {
          // Can only use this page if they're an admin.
          setIsLoggedIn(() => {
            return { state: false, pending: false };
          });
          router.replace("/");
          return;
        }

        // Fetch all users.
        const res2 = await fetch(`${window.location.origin}/api/users`, {
          method: "GET",
          cache: "no-cache",
          credentials: "include",
        });

        if (res2.ok) {
          const data: Array<{ user_id: number; username: string }> = await res2.json();
          setUsers(() => {
            return { state: data, pending: false };
          }); // Assumes data is an array of { user_id, username }
        }
      } else {
        // If the user is not logged in , return them to home page.
        setIsLoggedIn((prev) => {
          return { ...prev, pending: false };
        });
        router.replace("/");
        return;
      }
    }

    GetSession();
  }, [router]);

  function FormAction(formData: FormData) {
    async function SendTicket() {
      if (formData == null) {
        setSelectedUserIds([]);
        return;
      }

      if (
        formData.get("title")?.toString() == " " ||
        formData.get("description")?.toString() == " " ||
        formData.get("title")?.toString() == null ||
        formData.get("description")?.toString() == null ||
        selectedUserIds.length == 0
      ) {
        setSelectedUserIds([]);
        setMessage("Form Error. Please provide some content to the fields.");
      }

      const currentUser = users.state.find((user) => user.username === username);
      const currentUserId = currentUser?.user_id;

      const body = {
        title: formData.get("title")?.toString(),
        description: formData.get("description")?.toString(),
        status: "Open",
        assigned_user_ids: Array.from(new Set([...selectedUserIds, currentUserId])).filter(Boolean),
      };

      const res = await fetch(`${window.location.origin}/api/tickets`, {
        method: "POST",
        cache: "no-cache",
        credentials: "include",
        body: JSON.stringify(body),
        headers: {
          "Content-Type": "application/json",
        },
      });

      const er = await res.json();

      if (res.ok) {
        setMessage("Successfully created ticket!");
      } else {
        setMessage(`Server Response: ${JSON.stringify(er)}`);
      }
      setSelectedUserIds([]);
    }
    SendTicket();
  }

  if (isLoggedIn.pending == true) {
    return (
      <p className='flex w-full h-full items-center justify-center text-center italic text-2xl'>
        Checking Credentials...
      </p>
    );
  } else if (isLoggedIn.pending == false && isLoggedIn.state == false) {
    return (
      <p className='flex w-full h-full items-center justify-center text-center italic text-2xl'>
        Not Logged In... Not authorised, being redirected.
      </p>
    );
  }

  return (
    <div className='flex w-full h-full items-center justify-center flex-col gap-6'>
      <h1 className='flex text-4xl underline pb-8'>Create A Ticket</h1>
      <form action={FormAction} className='flex flex-col gap-4 w-[70%] h-fit'>
        <div className='flex flex-row gap-4 items-center w-full'>
          <label htmlFor='title' className='flex text-lg w-[20%]'>
            Title
          </label>
          <input
            type='text'
            name='title'
            required
            className='flex border-[1px] border-gray-600 rounded-sm shadow-md px-4 py-2 w-[80%]'
            placeholder='Enter title...'
          />
        </div>
        <div className='flex flex-row gap-4 items-center w-full'>
          <label htmlFor='title' className='flex text-lg w-[20%]'>
            Description
          </label>
          <textarea
            name='description'
            rows={5}
            required
            className='flex border-[1px] border-gray-600 rounded-sm shadow-md px-4 py-2 w-[80%]'
            placeholder='Enter description...'
          />
        </div>
        <div className='flex flex-row gap-4 w-full items-center'>
          <label className='flex text-lg w-[20%]'>Assign To</label>
          {users.pending == false ? (
            <div className='grid grid-cols-4 gap-2 w-[80%] overflow-y-auto border border-gray-300 rounded p-2 items-center justify-center'>
              {users.state
                .filter((user) => user.username !== username)
                .map((user) => (
                  <label key={user.user_id} className='flex items-center gap-2 text-sm'>
                    <input
                      type='checkbox'
                      value={user.user_id}
                      checked={selectedUserIds.includes(user.user_id)}
                      onChange={(e) => {
                        const id = parseInt(e.target.value);
                        setSelectedUserIds((prev) =>
                          e.target.checked ? [...prev, id] : prev.filter((uid) => uid !== id)
                        );
                      }}
                    />
                    {user.username}
                  </label>
                ))}
            </div>
          ) : (
            <p className='flex w-[80%] text-md italic items-center'>Loading users...</p>
          )}
        </div>
        <button
          type='submit'
          className='flex px-4 py-2 border-[1px] border-gray-500 rounded-sm shadow-md bg-blue-200 hover:bg-blue-400 hover:underline text-center items-center justify-center w-[30%] self-end'
        >
          Submit
        </button>
        <p className='flex italic text-sm self-end p-2'>{message}</p>
      </form>
    </div>
  );
}
