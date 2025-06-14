"use client";

import { useEffect, useState } from "react";
import { Ticket } from "../page";
import { useRouter } from "next/navigation";
import DeleteIcon from "../../../../public/delete.svg";
import Image from "next/image";

export type Comment = {
  author_id: number;
  author_username: string;
  content: string;
  created_at: string;
  id: number;
};

export default function TicketPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const [forceReload, setForceReload] = useState<boolean>(false);
  const [ticketId, setTicketId] = useState<number | null>(null);
  const [comments, setComments] = useState<{ state: Array<Comment>; pending: boolean }>({ state: [], pending: true });

  const [isLoggedIn, setIsLoggedIn] = useState({ state: false, pending: true });
  const [username, setUsername] = useState<string>("");
  const [userId, setUserId] = useState<number>(0);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [ticket, setTicket] = useState<{ state: Ticket | null; pending: boolean }>({ state: null, pending: true });

  useEffect(() => {
    async function GetSession() {
      // This stops the usage of data in the client roll out before it's been fetched.
      setIsLoggedIn((prev) => {
        return { ...prev, pending: true };
      });

      setTicket((prev) => {
        return { ...prev, pending: true };
      });

      setComments((prev) => {
        return { ...prev, pending: true };
      });

      // Check session / aka, if the user is logged in.
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/session`, {
        method: "GET",
        cache: "no-cache",
        credentials: "include",
      });

      if (res.status != 200) {
        setIsLoggedIn(() => {
          return { state: false, pending: false };
        });

        router.replace("/"); // If the user is not logged in , return them to home page.
        return;
      } else {
        setIsLoggedIn(() => {
          return { state: true, pending: false };
        });
      }

      const { role, username, user_id }: { role: string; username: string; user_id: number } = await res.json();

      // Mark whether the user is an admin, may change the options shown.
      if (role == "admin") {
        setIsAdmin(() => {
          return true;
        });
      }

      if (username != null) {
        setUsername(username);
      }

      if (user_id != 0 && user_id != null) {
        setUserId(user_id);
      }

      // Get route id
      const id = Number((await params).id);
      console.log("Route id: ", id);
      setTicketId(() => {
        return id;
      });

      // Fetch ticket.
      const res2 = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tickets/${id}`, {
        method: "GET",
        cache: "no-cache",
        credentials: "include",
      });

      const ticket = (await res2.json()) as Ticket;
      setTicket(() => {
        return { state: ticket, pending: false };
      });

      // Get Comments
      const res3 = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/tickets/${id}/comments`, {
        method: "GET",
        cache: "no-cache",
        credentials: "include",
      });

      const comments = (await res3.json()) as Array<{
        author_id: number;
        content: string;
        created_at: string;
        id: number;
      }>;

      const master_comments: Array<Comment> = [];

      // Get Comment Authors
      for (let index = 0; index < comments.length; index++) {
        const comment = comments[index];
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/${comment.author_id}`, {
          method: "GET",
          cache: "force-cache",
          credentials: "include",
        });
        const author = (await res.json()).username as string;
        master_comments.push({ ...comment, author_username: author });
      }

      setComments(() => {
        return { state: master_comments, pending: false };
      });
    }

    GetSession();
  }, [forceReload]);

  function Comment({ data }: { data: Comment }) {
    if (ticket.state == null) return null;

    return (
      <div className='flex w-full h-fit flex-row border-[1px] border-gray-300 rounded-sm shadow-sm px-4 py-2 items-center'>
        <div className='flex w-[95%] h-fit flex-col gap-2 items-center'>
          <p className='flex text-md self-start'>{data.content}</p>
          <span className='flex h-[1px] w-[90%] bg-gray-300'></span>
          <div className='flex w-full h-fit flex-row justify-around'>
            <h4 className='flex'>Author: {data.author_username}</h4>
            <h4 className='flex'>Date Written: {data.created_at}</h4>
          </div>
        </div>
        {userId == ticket.state.creator_id || username === data.author_username ? (
          <button
            className='flex w-[5%] h-full flex-col items-center justify-center bg-red-300 rounded-md shadow-md hover:bg-red-500 hover:cursor-pointer'
            onClick={() => {
              fetch(`${process.env.NEXT_PUBLIC_API_URL}/comments/${data.id}`, {
                method: "DELETE",
                cache: "default",
                credentials: "include",
              });
              setForceReload((prev) => {
                return !prev;
              });
            }}
          >
            <Image src={DeleteIcon} alt='Delete Icon' />
          </button>
        ) : null}
      </div>
    );
  }

  // Preload checks
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

  if (ticket.pending == true || ticket.state == null) {
    return (
      <p className='flex w-full h-full items-center justify-center text-center italic text-2xl'>
        Loading ticket data...
      </p>
    );
  }

  if (comments.pending == true) {
    return (
      <p className='flex w-full h-full items-center justify-center text-center italic text-2xl'>
        Loading comments data...
      </p>
    );
  }

  // Main return
  return (
    <div className='flex w-[80%] h-full flex-col gap-4 justify-center items-center'>
      <h1 className='flex text-4xl underline bold'>{ticket.state.title}</h1>
      <p className='flex text-lg'>{ticket.state.description}</p>
      <span className='flex h-[1px] w-[90%] bg-gray-300'></span>
      <h2 className='flex text-2xl self-start'>Comments:</h2>
      <div className='flex w-full h-fit gap-4 flex-col'>
        {comments.state.map((comment) => {
          return <Comment data={comment} key={comment.id} />;
        })}
      </div>
    </div>
  );
}
