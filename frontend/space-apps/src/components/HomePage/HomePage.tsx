'use client'

import { useState, useMemo, useRef, useEffect } from 'react'
import Link from 'next/link'
import { Input } from "@/components/HomePage/ui/input"
import { Button } from "@/components/HomePage/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/HomePage/ui/card"
import { Badge } from "@/components/HomePage/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/HomePage/ui/select"
import { ScrollArea } from "@/components/HomePage/ui/scroll-area"
import { Search, Send } from "lucide-react"

// This would typically come from an API or database
const papers = [
  { accessionNumber: 'GSE123456', title: 'Gene Expression in Drosophila melanogaster', organism: 'Drosophila melanogaster', slug: 'OSD-379' },
  { accessionNumber: 'GSE789012', title: 'Transcriptome Analysis of Arabidopsis thaliana', organism: 'Arabidopsis thaliana', slug: 'gse789012' },
  { accessionNumber: 'GSE345678', title: 'Mouse Brain Cell Atlas', organism: 'Mus musculus', slug: 'gse345678' },
  { accessionNumber: 'GSE901234', title: 'Human Liver Cancer Study', organism: 'Homo sapiens', slug: 'gse901234' },
  { accessionNumber: 'GSE567890', title: 'Zebrafish Embryonic Development', organism: 'Danio rerio', slug: 'gse567890' },
]

export function HomePage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedOrganism, setSelectedOrganism] = useState('')
  const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'bot'; content: string }[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const chatEndRef = useRef<HTMLDivElement>(null)

  const organisms = useMemo(() => {
    return ['All', ...new Set(papers.map(paper => paper.organism))]
  }, [])

  const filteredPapers = papers.filter(paper =>
    (paper.accessionNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
    paper.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    paper.organism.toLowerCase().includes(searchTerm.toLowerCase())) &&
    (selectedOrganism === '' || selectedOrganism === 'All' || paper.organism === selectedOrganism)
  )

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      setChatMessages([...chatMessages, { role: 'user', content: inputMessage }])
      // Here you would typically send the message to your chatbot API
      // and then add the response to the chat messages
      setTimeout(() => {
        setChatMessages(prev => [...prev, { role: 'bot', content: 'This is a placeholder response from the chatbot.' }])
      }, 1000)
      setInputMessage('')
    }
  }

  return (
    <div className="container mx-auto p-4 flex flex-col h-screen">
      <h1 className="text-4xl font-bold mb-6 text-[#105bd8]">Scientific Paper Explorer</h1>
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="flex gap-2 flex-1">
          <Input
            type="text"
            placeholder="Search papers..."
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
        {filteredPapers.map((paper) => (
          <Link href={`/project/${paper.slug}`} key={paper.slug} className="block h-[200px]">
            <Card className="flex flex-col h-full transition-colors hover:bg-gray-50 cursor-pointer">
              <CardHeader className="flex-grow">
                <CardTitle className="text-lg">
                  {paper.accessionNumber}
                </CardTitle>
                <CardDescription className="line-clamp-2">{paper.title}</CardDescription>
              </CardHeader>
              <CardFooter>
                <Badge variant="secondary">{paper.organism}</Badge>
              </CardFooter>
            </Card>
          </Link>
        ))}
      </div>
      {filteredPapers.length === 0 && (
        <p className="text-center text-gray-500 mt-4">No papers found matching your search criteria.</p>
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
  )
}