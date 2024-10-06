"use client";

import { useState, useMemo, useRef, useEffect } from 'react';
import Link from 'next/link';
import { Input } from "@/components/HomePage/ui/input";
import { Button } from "@/components/HomePage/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/HomePage/ui/card";
import { Badge } from "@/components/HomePage/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/HomePage/ui/select";
import { ScrollArea } from "@/components/HomePage/ui/scroll-area";
import { Search, Send } from "lucide-react";

export function HomePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOrganism, setSelectedOrganism] = useState('');
  const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'bot'; content: string }[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [projects, setProjects] = useState([]); // Initialized as an empty array

  useEffect(() => {
    async function fetchProjects() {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/Project/all');

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setProjects(data);
      } catch (error) {
        console.error('Error fetching project data:', error);
      }
    }

    fetchProjects();
  }, []);

  const organisms = useMemo(() => {
    return ['All', ...new Set(projects.map(project => project.organism))];
  }, [projects]);

  const filteredProjects = useMemo(() => {
    return projects.filter(project =>
      (project.accession.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.organism.toLowerCase().includes(searchTerm.toLowerCase())) &&
      (selectedOrganism === '' || selectedOrganism === 'All' || project.organism === selectedOrganism)
    );
  }, [projects, searchTerm, selectedOrganism]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleSendMessage = async () => {
    if (inputMessage.trim()) {
      // Add the user's message to the chat
      setChatMessages([...chatMessages, { role: 'user', content: inputMessage }]);
      const userMessage = inputMessage;
      setInputMessage(''); // Clear the input field
  
      try {
        // Send the user's message to the Flask API
        const response = await fetch('http://127.0.0.1:5000/api/chatbot', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: userMessage }),
        });
  
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
  
        const data = await response.json();
  
        // Add the chatbot's response to the chat
        setChatMessages((prev) => [...prev, { role: 'bot', content: data.response }]);
      } catch (error) {
        console.error('Error communicating with chatbot API:', error);
        // Optionally, display an error message in the chat
        setChatMessages((prev) => [
          ...prev,
          { role: 'bot', content: 'Sorry, there was an error processing your message.' },
        ]);
      }
    }
  };

  if (projects.length === 0) {
    return <p>Loading...</p>;
  }

  return (
    <div className="container mx-auto p-4 flex flex-col h-screen">
      <h1 className="text-4xl font-bold mb-6 text-[#105bd8]">Space Apps</h1>
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="flex gap-2 flex-1">
          <Input
            type="text"
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-grow"
          />
          <Button variant="outline" size="icon">
            <Search className="h-4 w-4" />
            <span className="sr-only">Search</span>
          </Button>
        </div>
        <Select value={selectedOrganism} onValueChange={setSelectedOrganism}>
          <SelectTrigger className="w-full md:w-[200px]">
            <SelectValue placeholder="Filter by organism" />
          </SelectTrigger>
          <SelectContent>
            {organisms.map((organism) => (
              <SelectItem key={organism} value={organism}>
                {organism}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 flex-grow overflow-auto mb-4">
        {filteredProjects.map((project) => (
          <Link href={`/project/${project.slug}`} key={project.slug} className="block h-[200px]">
            <Card className="flex flex-col h-full transition-colors hover:bg-gray-50 cursor-pointer">
              <CardHeader className="flex-grow">
                <CardTitle className="text-lg">
                  {project.accession}
                </CardTitle>
                <CardDescription className="line-clamp-2">{project.title}</CardDescription>
              </CardHeader>
              <CardFooter>
                <Badge variant="secondary">{project.organism}</Badge>
              </CardFooter>
            </Card>
          </Link>
        ))}
      </div>
      {filteredProjects.length === 0 && (
        <p className="text-center text-gray-500 mt-4">No projects found matching your search criteria.</p>
      )}
      <div className="mt-auto">
        <Card className="mb-4 bg-gray-100">
          <CardContent className="p-4">
            <ScrollArea className="h-[200px] w-full pr-4">
              {chatMessages.map((message, index) => (
                <div key={index} className={`mb-2 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <span className={`inline-block p-2 rounded-lg ${message.role === 'user' ? 'bg-blue-100' : 'bg-white'}`}>
                    {message.content}
                  </span>
                </div>
              ))}
              <div ref={chatEndRef} />
            </ScrollArea>
          </CardContent>
        </Card>
        <div className="flex gap-2">
          <Input
            type="text"
            placeholder="Type your message..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            className="flex-grow"
          />
          <Button onClick={handleSendMessage}>
            <Send className="h-4 w-4 mr-2" />
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}
