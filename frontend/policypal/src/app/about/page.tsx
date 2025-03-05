'use client';
import React from 'react';
//import Navbar from '@/components/Navbar';
import Image from 'next/image';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-black mb-4">About Policy Pal</h1>
          <p className="mt-4 text-black">
            Hello! Our goal here at Policy Pal is to make the legislative branch of government a little more transparent,
            so that everyone is able to easily keep up with politics! We believe it&#39;s important to stay informed, and even better
            for American citizens to be able to understand what their local representatives are actually doing when they become elected.
          </p>
          <br/>
          <h3 className="text-2xl font-bold text-black mb-4">What is Congress?</h3>
          <p className="mt-4 text-black">
            While it may seem as if the President holds all the power, there are actually <b>three</b> main branches of government. Congress 
            is part of the legislative branch, which means they are the ones who can change, add, or repeal laws. It is made up of
            two separate bodies:
            </p>
            <p className="mt-4 text-black">
                <strong>House of Representatives: </strong>
            </p>
            <ul className="list-disc ml-6 text-black">

                    <li>435 members</li>
                    <li>Seats are allocated based on each state&#39;s population</li>
            </ul>
            <p className="mt-4 text-black">
                <strong>Senate: </strong>
            </p>
            <ul className="list-disc ml-6 text-black">
                <li>100 members</li>
                <li>Seats are allocated based on each state&#39;s population</li>
            </ul>
            
            <p className="mt-4 text-black">
            Congress additionally holds &#39;the power of the purse&#39;, which means they decide how American tax dollars are spent. This is a lot of power! 
            
            That&#39;s why for any bill to pass, it needs to pass through two houses each containing representatives of the American states.
            The House of Representatives and Senate are collectively referred to as &#34;Congress&#34;. 
          </p>
          <div className="my-6">
            <Image
              src="/infographic.jpg"
              alt="Infographic on How a Bill Becomes a Law"
              width={600}
              height={300}
              className="rounded shadow"
            />
          </div>
          <br/>
          <p className="mt-4 text-black">
            As you can see above, this is a complicated process! It&#39;s a long time before bills become laws, but by voting for representatives 
            with similar values to your own, contacting them (phone, email, etc) to have them vote on bills you&#39;re passionate about, and participating
            in local government will let you personally help America grow the way that you want it to. 
          </p>
          <br/>
          <br/>
          <h3 className="text-2xl font-bold text-black mb-4">So, what do the other branches of government do?</h3>
          <p className="mt-4 text-black-700">
            There are two other branches of government, the executive branch, and the judicial branch.
            First, the judicial branch can revoke unconstitutional laws, and has the power to interpret vague laws. 
            For example, gun rights in America have been hotly contested for a long time, and the Constitution is vague in what it allows.
            The court system, with the Supreme court at the top, can interpret whether laws restricting or allowing all guns is unconstitutional.

            The last branch of government is the executive branch. The executive branch contains the President, who has the power to veto bills, 
            unless they passed through Congress with a 2/3 majority in both houses. The President can also approve bills into law that 
            passed Congress with a simple 1/2 majority. The President also has the power to create executive orders, separate from Congress!

          </p>
          <div className="my-6">
            <Image
              src="/gov_Branches.jpg"
              alt="Overview of Government Branches"
              width={400}
              height={200}
              className="rounded shadow"
            />
          </div>
          <br/>
          <h3 className="text-2xl font-bold text-black-900 mb-4">Wait, Executive Orders aren&#39;t Laws?</h3>
          <p className="mt-4 text-black">
            From the <a href="https://www.aclu.org/news/privacy-technology/what-is-an-executive-order-and-how-does-it-work"
               className="text-blue-500 underline hover:text-blue-700">American Civil Liberties Union</a>:
        </p>
            <blockquote className="bg-gray-100 border-l-4 border-blue-500 pl-4 py-2 italic my-8">
                <p>
  
            &#34;Article II of the Constitution vests the president with executive power over the government, including the obligation to 
            &#34;take care that the laws be faithfully executed.&#34; An executive order is a written directive, signed by the president, 
            that orders the government to take specific actions to ensure &#34;the laws be faithfully executed.&#34; It might mean telling 
            the Department of Education to implement a certain rule, or declaring a new policy priority. Executive orders, however, 
            cannot override federal laws and statutes.
                <br/>
                ...
                <br/>
            With an executive order, the president can&#39;t write a new statute, but an order can tell federal agencies how to implement 
            a statute. For example, Congress can declare a certain drug legal or illegal. But with an executive order, the president 
            can tell the Department of Justice if prosecuting certain drug cases is a priority or not.&#34;
            <br/>
            </p>
            <footer className="mt-2 text-right">— ACLU</footer>
            </blockquote>
            <br/>
            <br/>
          <h3 className="text-2xl font-bold text-black-900 mb-4">Contact Us/Other Resources</h3>
          <p className="mt-4 text-black">
            Thanks so much for checking us out! If you have any other questions about the US government, check{' '}
            <a href="https://www.youtube.com/watch?v=lrk4oY7UxpQ&list=PL8dPuuaLjXtOfse2ncvffeelTrqvhrz8H"
               className="text-blue-500 underline hover:text-blue-700">here</a>,
            and if there&#39;s bugs or have ideas for additional features, feel free to reach out{' '} 
            <a href="https://screamintothevoid.com/" className="text-blue-500 underline hover:text-blue-700">here</a>!
          </p>
        </div>
      </main>
    </div>
  );
}
