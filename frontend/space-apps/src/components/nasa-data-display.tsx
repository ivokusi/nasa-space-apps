'use client'

import { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import dynamic from 'next/dynamic'

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

const nasaBlue = '#0B3D91'

interface SectionProps {
  title: string
  content: string | React.ReactNode
}

interface ChatMessage {
  text: string
  isUser: boolean
}

interface Sample {
  id: string
  value: number | string
  additionalData: {
    [key: string]: string | number
  }
}

const ExpandableSection: React.FC<SectionProps> = ({ title, content }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div 
      className="mb-4 cursor-pointer" 
      onMouseEnter={() => setIsExpanded(true)} 
      onMouseLeave={() => setIsExpanded(false)}
    >
      <h3 className="text-lg font-semibold mb-2" style={{ color: nasaBlue }}>{title}</h3>
      <div 
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isExpanded ? 'max-h-[1000px]' : 'max-h-0'
        }`}
      >
        {typeof content === 'string' ? (
          <p className="text-muted-foreground">{content}</p>
        ) : (
          content
        )}
      </div>
    </div>
  )
}

const contactInfo = [
  { firstName: "John", lastName: "Doe", email: "john.doe@nasa.gov", affiliation: "NASA JPL", role: "Project Manager" },
  { firstName: "Jane", lastName: "Smith", email: "jane.smith@nasa.gov", affiliation: "NASA Ames", role: "Lead Scientist" },
  { firstName: "Mike", lastName: "Johnson", email: "mike.johnson@nasa.gov", affiliation: "NASA Glenn", role: "Systems Engineer" },
]

const protocols = [
  { name: "Data Collection Protocol", description: "Standardized procedures for gathering and recording mission data to ensure consistency and accuracy across all instruments and observations." },
  { name: "Transmission Security Protocol", description: "Encryption and verification methods to secure data transmission between the spacecraft and Earth, protecting sensitive information from interception or corruption." },
  { name: "Planetary Protection Protocol", description: "Guidelines to prevent contamination of celestial bodies with Earth-based microorganisms, preserving the integrity of potential extraterrestrial environments for scientific study." },
  { name: "Emergency Response Protocol", description: "Predefined procedures for handling unexpected events or malfunctions, ensuring rapid and effective responses to maintain mission safety and continuity." },
  { name: "Sample Collection Protocol", description: "Detailed procedures for collecting, storing, and preserving samples from celestial bodies, ensuring their scientific integrity during the return journey to Earth." },
  { name: "Communication Protocol", description: "Standardized methods for maintaining clear and efficient communication between the spacecraft and mission control, including procedures for handling communication delays." },
]

const payload = {
  identifier: "MPSE-2023",
  name: "Multi-Purpose Space Explorer",
  description: "Advanced spacecraft equipped with a suite of scientific instruments designed for deep space exploration, including high-resolution cameras, spectrometers, and particle detectors."
}

const mission = {
  identifier: "DSE-001",
  start: "2025-07-15",
  end: "2035-12-31"
}

const project = {
  projectType: "Space Exploration",
  flightProgram: "Deep Space Initiative",
  experimentPlatform: "Orbital and Planetary",
  sponsoringAgency: "NASA",
  nasaCenter: "Jet Propulsion Laboratory",
  fundingSource: "N/A"
}

const factors = [
  "Solar radiation",
  "Gravitational forces from large planets",
  "Long-distance communication challenges",
  "Extreme temperature variations",
  "Micrometeoroid impacts",
  "Cosmic radiation exposure"
]

const randomResponses = [
  "Fascinating question! Let me process that for a moment.",
  "That's an interesting point. Here's what I know about it...",
  "I'm glad you asked. The data suggests...",
  "According to our mission parameters, we can say that...",
  "That's a complex topic. Let me break it down for you.",
  "Based on our current understanding of space exploration...",
  "Great question! Our latest research indicates...",
  "Let me consult my database... Here's what I found:",
  "That's an area of ongoing study. Current theories suggest...",
  "Excellent inquiry! Here's the most up-to-date information we have:"
]

// Dummy data
const dummyData: Sample[] = Array.from({ length: 100 }, (_, i) => ({
  id: `sample-${i + 1}`,
  value: ['Y', 'U', 'I', 'O', 'J'][Math.floor(Math.random() * 5)],
  additionalData: {
    temperature: Math.random() * 100,
    pressure: Math.random() * 10,
    radiation: Math.random() * 1000,
    composition: ['Rock', 'Ice', 'Gas', 'Dust'][Math.floor(Math.random() * 4)]
  }
}))

const qualitativeData: Sample[] = Array.from({ length: 100 }, (_, i) => ({
  id: `qual-sample-${i + 1}`,
  value: ['R', 'V', 'D', 'S'][Math.floor(Math.random() * 4)],
  additionalData: {
    size: ['Small', 'Medium', 'Large'][Math.floor(Math.random() * 3)],
    color: ['Red', 'Blue', 'Green', 'Yellow'][Math.floor(Math.random() * 4)],
    texture: ['Smooth', 'Rough', 'Porous'][Math.floor(Math.random() * 3)],
    origin: ['Mars', 'Jupiter', 'Saturn', 'Asteroid Belt'][Math.floor(Math.random() * 4)]
  }
}))

const numericalColumns = ['Y', 'U', 'I', 'O', 'J']
const qualitativeColumns = ['R', 'V', 'D', 'S']

export function NasaDataDisplay() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const [selectedColumn, setSelectedColumn] = useState<string>(numericalColumns[0])
  const [showPieChart, setShowPieChart] = useState(false)
  const [selectedSamples, setSelectedSamples] = useState<Sample[]>([])

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  useEffect(() => {
    setSelectedColumn(showPieChart ? qualitativeColumns[0] : numericalColumns[0])
    setSelectedSamples([])
  }, [showPieChart])

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      const userMessage: ChatMessage = { text: inputMessage, isUser: true }
      setMessages(prevMessages => [...prevMessages, userMessage])
      setInputMessage('')

      // Simulate chatbot response
      setTimeout(() => {
        const botResponse: ChatMessage = { 
          text: randomResponses[Math.floor(Math.random() * randomResponses.length)], 
          isUser: false 
        }
        setMessages(prevMessages => [...prevMessages, botResponse])
      }, 1000)
    }
  }

  const getChartData = () => {
    const data = (showPieChart ? qualitativeData : dummyData).reduce((acc, item) => {
      const value = item.value
      acc[value] = (acc[value] || 0) + 1
      return acc
    }, {} as Record<string | number, number>)

    return Object.entries(data).map(([name, value]) => ({ name, value }))
  }

  const handleChartClick = (event: any) => {
    if (event.points && event.points.length > 0) {
      const clickedValue = event.points[0].x || event.points[0].label
      const samples = (showPieChart ? qualitativeData : dummyData).filter(
        sample => sample.value === clickedValue
      )
      setSelectedSamples(samples)
    }
  }

  const renderChart = () => {
    const data = getChartData()

    if (showPieChart) {
      return (
        <Plot
          data={[
            {
              values: data.map(item => item.value),
              labels: data.map(item => item.name),
              type: 'pie',
              marker: { colors: [nasaBlue, '#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD'] },
            },
          ]}
          layout={{
            title: `Distribution of ${selectedColumn}`,
            autosize: true,
            margin: { l: 50, r: 50, b: 50, t: 50, pad: 4 },
          }}
          onClick={handleChartClick}
          useResizeHandler={true}
          style={{ width: '100%', height: '100%' }}
        />
      )
    } else {
      return (
        <Plot
          data={[
            {
              x: data.map(item => item.name),
              y: data.map(item => item.value),
              type: 'bar',
              marker: { color: nasaBlue },
            },
          ]}
          layout={{
            title: `Distribution of ${selectedColumn}`,
            xaxis: { title: selectedColumn },
            yaxis: { title: 'Count' },
            autosize: true,
            margin: { l: 50, r: 50, b: 50, t: 50, pad: 4 },
          }}
          onClick={handleChartClick}
          useResizeHandler={true}
          style={{ width: '100%', height: '100%' }}
        />
      )
    }
  }

  return (
    <div className="container mx-auto p-4">
      <div className="grid gap-6">
        <Card className="w-full">
          <CardHeader>
            <CardTitle className="text-2xl font-bold" style={{ color: nasaBlue }}>
              NASA Mission Data
            </CardTitle>
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mt-2">
              <p className="text-sm text-muted-foreground">Accession Number: NASA-2023-001</p>
              <Badge variant="secondary" className="mt-2 sm:mt-0">
                Organism: Homo sapiens
              </Badge>
            </div>
          </CardHeader>
        </Card>

        <div className="grid md:grid-cols-3 gap-0">
          <Card className="w-full md:col-span-2 rounded-r-none border-r-0">
            <CardHeader className="border-b-0">
              <CardTitle className="text-xl font-semibold" style={{ color: nasaBlue }}>Data Visualization</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-4 flex items-center justify-between">
                <Select onValueChange={setSelectedColumn} value={selectedColumn}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select parameter" />
                  </SelectTrigger>
                  <SelectContent>
                    {(showPieChart ? qualitativeColumns : numericalColumns).map((column) => (
                      <SelectItem key={column} value={column}>
                        {column}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="chart-toggle"
                    checked={showPieChart}
                    onCheckedChange={setShowPieChart}
                  />
                  <Label htmlFor="chart-toggle">Show Pie Chart</Label>
                </div>
              </div>
              <div className="aspect-video bg-gray-200 flex items-center justify-center rounded-md">
                {renderChart()}
              </div>
              {selectedSamples.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-lg font-semibold mb-2">Selected Samples</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedSamples.map((sample) => (
                      <Dialog key={sample.id}>
                        <DialogTrigger asChild>
                          <Button variant="outline">{sample.id}</Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Sample Details: {sample.id}</DialogTitle>
                          </DialogHeader>
                          <div className="mt-4">
                            <p><strong>Value:</strong> {sample.value}</p>
                            {Object.entries(sample.additionalData).map(([key, value]) => (
                              <p key={key}><strong>{key}:</strong> {value}</p>
                            ))}
                          </div>
                        </DialogContent>
                      </Dialog>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="w-full rounded-l-none border-l-0 flex flex-col">
            <CardHeader className="border-b-0">
              <CardTitle className="text-xl font-semibold" style={{ color: nasaBlue }}>Chatbot</CardTitle>
            </CardHeader>
            <CardContent className="flex-grow flex flex-col">
              <ScrollArea className="flex-grow mb-4 p-4 bg-gray-100 rounded-md h-[400px]">
                {messages.map((msg, index) => (
                  <div key={index} className={`mb-2 ${msg.isUser ? 'text-right' : 'text-left'}`}>
                    <span className={`inline-block p-2 rounded-lg ${msg.isUser ? 'bg-blue-500 text-white' : 'bg-gray-300 text-gray-800'}`}>
                      {msg.text}
                    </span>
                  </div>
                ))}
              </ScrollArea>
              <div className="flex gap-2 mt-auto">
                <Input 
                  placeholder="Type your message..." 
                  className="flex-grow" 
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                />
                <Button style={{ backgroundColor: nasaBlue }} onClick={handleSendMessage}>Send</Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="w-full">
          <CardContent className="pt-6">
            <ExpandableSection 
              title="Description" 
              content="This NASA mission aims to explore the outer reaches of our solar system, gathering crucial data about the composition and behavior of distant celestial bodies. The mission utilizes cutting-edge technology and a multidisciplinary approach to push the boundaries of our understanding of space."
            />
            <ExpandableSection 
              title="Factors" 
              content={
                <div className="bg-gray-50 p-4 rounded-md">
                  <div className="grid grid-cols-2 gap-4">
                    {factors.map((factor, index) => (
                      <div key={index} className="flex items-start">
                        <div className="w-2 h-2 rounded-full mt-2 mr-2 flex-shrink-0" style={{ backgroundColor: nasaBlue }}></div>
                        <span className="text-sm text-muted-foreground">{factor}</span>
                      </div>
                    ))}
                  </div>
                </div>
              }
            />
            <ExpandableSection 
              title="Project" 
              content={
                <div className="bg-gray-50 p-4 rounded-md">
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(project).map(([key, value]) => (
                      value !== "N/A" && (
                        <div key={key}>
                          <h4 className="text-sm font-semibold mb-1 capitalize" style={{ color: nasaBlue }}>
                            {key.split(/(?=[A-Z])/).join(" ")}
                          </h4>
                          <p className="text-sm text-muted-foreground">{value}</p>
                        </div>
                      )
                    ))}
                  </div>
                </div>
              }
            />
            <ExpandableSection 
              title="Mission" 
              content={
                <div className="bg-gray-50 p-4 rounded-md">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <h4 className="text-sm font-semibold mb-1" style={{ color: nasaBlue }}>Identifier</h4>
                      <p className="text-sm text-muted-foreground">{mission.identifier}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold mb-1" style={{ color: nasaBlue }}>Start Date</h4>
                      <p className="text-sm text-muted-foreground">{mission.start}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold mb-1" style={{ color: nasaBlue }}>End Date</h4>
                      <p className="text-sm text-muted-foreground">{mission.end}</p>
                    </div>
                  </div>
                </div>
              }
            />
            <ExpandableSection 
              title="Payload" 
              content={
                <div className="bg-gray-50 p-4 rounded-md">
                  <div className="flex items-center mb-2">
                    <span className="text-sm font-medium text-muted-foreground mr-2">{payload.identifier}</span>
                    <h4 className="font-semibold" style={{ color: nasaBlue }}>{payload.name}</h4>
                  </div>
                  <p className="text-sm text-muted-foreground">{payload.description}</p>
                </div>
              }
            />
            <ExpandableSection 
              title="Protocols" 
              content={
                <div>
                  {protocols.map((protocol, index) => (
                    <div 
                      key={index} 
                      className="bg-gray-50 p-4 rounded-md mb-4 transition-colors duration-200 ease-in-out hover:bg-gray-100"
                    >
                      <h4 className="font-semibold mb-2" style={{ color: nasaBlue }}>{protocol.name}</h4>
                      <p className="text-sm text-muted-foreground">{protocol.description}</p>
                    </div>
                  ))}
                </div>
              }
            />
            <ExpandableSection 
              title="Contact Information" 
              content={
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Affiliation</TableHead>
                      <TableHead>Role</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {contactInfo.map((contact, index) => (
                      <TableRow key={index}>
                        <TableCell>{`${contact.firstName} ${contact.lastName}`}</TableCell>
                        <TableCell>{contact.email}</TableCell>
                        <TableCell>{contact.affiliation}</TableCell>
                        <TableCell>{contact.role}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              }
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}