import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import HomeIcon from "../../public/home.svg";
import Image from "next/image";
import Link from "next/link";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Subjex Ticket Management System",
  description: "Made using Flask and React via NextJS",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang='en'>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <main className='flex flex-col w-[100vw] h-[100vh] p-2'>
          <Link
            href={"/"}
            className='flex w-fit h-fit px-4 py-2 border-black border-[1px] shadow-sm rounded-sm hover:bg-gray-100 hover:cursor-pointer'
          >
            <Image src={HomeIcon} alt='Home Icon' />
          </Link>
          {children}
        </main>
      </body>
    </html>
  );
}
