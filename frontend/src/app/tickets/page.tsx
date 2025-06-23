"use client";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import ReloadIcon from "../../../public/reload.svg";

export type Ticket = {
  assigned_users: Array<{
    user_id: number;
    username: string;
  }>;
  creator_id: number;
  description: string;
  id: number;
  status: string;
  title: string;
};

export default function Tickets() {
  const router = useRouter();
  const [forceReload, setForceReload] = useState<boolean>(false);

  const [isLoggedIn, setIsLoggedIn] = useState({ state: false, pending: true });
  const [username, setUsername] = useState<string>("");
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [tickets, setTickets] = useState<{ state: Array<Ticket>; pending: boolean }>({ state: [], pending: true });
  const [hideClosed, setHideClosed] = useState<boolean>(true);

  useEffect(() => {
    async function GetSession() {
      // This stops the usage of data in the client roll out before it's been fetched.
      setIsLoggedIn((prev) => {
        return { ...prev, pending: true };
      });

      setTickets((prev) => {
        return { ...prev, pending: true };
      });

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/session`, {
        method: "GET",
        cache: "no-cache",
        credentials: "include",
      });

      if (res.status == 200) {
        setIsLoggedIn(() => {
          return { state: true, pending: false };
        });

        const { role, username }: { role: string; username: string } = await res.json();

        if (role == "admin") {
          setIsAdmin(() => {
            return true;
          });
        }

        if (username != null) {
          setUsername(username);
        }

        // Fetch tickets.
        const res2 = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tickets`, {
          method: "GET",
          cache: "no-cache",
          credentials: "include",
        });

        const tickets = (await res2.json()) as Array<Ticket>;

        setTickets(() => {
          return { state: tickets, pending: false };
        });
      } else {
        setIsLoggedIn((prev) => {
          return { ...prev, pending: false };
        });
        router.replace("/"); // If the user is not logged in , return them to home page.
        return;
      }
    }

    GetSession();
  }, [forceReload, router]);

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
    <div className='flex w-full h-full flex-col gap-4 items-center justify-center'>
      <div className='flex flex-row w-[80%] h-fit'>
        {isAdmin == true ? (
          <h1 className='flex w-full h-fit text-3xl bold'>{username}&apos;s Tickets (Admin)</h1>
        ) : (
          <h1 className='flex w-full h-fit text-3xl bold'>{username}&apos;s Tickets</h1>
        )}

        <div className='flex w-full h-fit flex-row gap-4 justify-end self-end'>
          <button
            className='flex'
            onClick={() => {
              setHideClosed((prev) => {
                return !prev;
              });
            }}
          >
            {hideClosed == true ? (
              <div className='px-4 py-2 bg-purple-200 hover:bg-purple-400 hover:underline rounded-sm shadow-md'>
                Hiding Closed Tickets
              </div>
            ) : (
              <div className='px-4 py-2 bg-pink-200 hover:bg-pink-400 hover:underline rounded-sm shadow-md'>
                Showing Closed Tickets
              </div>
            )}
          </button>
          <button
            className='flex text-1xl px-4 py-2 bg-blue-200 hover:bg-blue-400 hover:underline rounded-sm shadow-md'
            onClick={() =>
              setForceReload((prev) => {
                return !prev;
              })
            }
          >
            <Image src={ReloadIcon} alt='Reload Icon' />
          </button>
        </div>
      </div>
      {tickets.pending == true ? (
        <p className='flex w-full h-full items-center justify-center text-center italic text-2xl'>
          Fetching Tickets...
        </p>
      ) : (
        <div className='flex w-[80%] h-fit flex-col gap-4'>
          {tickets.state
            .filter((ticket) => !(ticket.status.toLowerCase() === "closed" && hideClosed))
            .map((ticket) => {
              return <Ticket data={ticket} key={ticket.id} />;
            })}
        </div>
      )}
    </div>
  );
}

function Ticket({ data }: { data: Ticket }) {
  return (
    <Link
      href={`tickets/lookup?id=${data.id}`}
      className={`flex flex-col gap-2 h-fit w-full border-gray-400 border-[1px] rounded-md shadow-sm p-4 hover:bg-gray-100 group hover:cursor-pointer`}
    >
      <div className='flex flex-row pr-4 justify-between items-center'>
        <h2 className={`flex text-2xl group-hover:underline`}>{data.title}</h2>
        {data.status.toLowerCase() === "open" ? (
          <h4 className='flex px-4 py-2 rounded-sm shadow-sm bg-green-300'>{data.status.toUpperCase()}</h4>
        ) : data.status.toLowerCase() === "closed" ? (
          <h4 className='flex px-4 py-2 rounded-sm shadow-sm bg-red-300'>{data.status.toUpperCase()}</h4>
        ) : data.status.toLowerCase() === "in review" ? (
          <h4 className='flex px-4 py-2 rounded-sm shadow-sm bg-orange-300'>{data.status.toUpperCase()}</h4>
        ) : null}
      </div>

      <div className='flex h-[1px] bg-gray-400 w-full shadow-sm'></div>
      <p className='flex text-md'>{data.description}</p>
    </Link>
  );
}
