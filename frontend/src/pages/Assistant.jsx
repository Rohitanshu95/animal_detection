import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Sparkles, Paperclip, Mic, ChevronLeft, Plus, MessageSquare, MoreHorizontal } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const SUGGESTED_QUERIES = [
  "Show incident trends for Elephants in 2024",
  "Summarize the latest poaching hotspot alert",
  "Compare conviction rates between Baripada and Similipal",
  "Draft a monthly report for the Director"
];

const Message = ({ role, content, reasoning }) => (
  <motion.div 
    initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
    className={`flex gap-4 mb-8 ${role === 'user' ? 'flex-row-reverse' : ''}`}
  >
    <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-sm ${role === 'ai' ? 'bg-gradient-to-br from-emerald-500 to-emerald-600' : 'bg-white border border-slate-200'}`}>
      {role === 'ai' ? <Bot className="w-6 h-6 text-white" /> : <User className="w-6 h-6 text-slate-600" />}
    </div>
    
    <div className={`max-w-[80%] lg:max-w-[70%] space-y-2`}>
      <div className={`p-5 rounded-2xl shadow-sm ${role === 'user' ? 'bg-emerald-600 text-white rounded-tr-sm' : 'bg-white border border-slate-100 text-slate-800 rounded-tl-sm'}`}>
        <p className="leading-relaxed whitespace-pre-wrap">{content}</p>
      </div>
      
      {reasoning && (
        <div className="bg-slate-50 rounded-xl border border-slate-100 overflow-hidden">
          <details className="group">
            <summary className="px-4 py-2 text-xs font-bold text-slate-500 uppercase tracking-wider cursor-pointer flex items-center gap-2 hover:bg-slate-100 transition-colors">
              <Sparkles className="w-3 h-3 text-emerald-500" /> 
              AI Reasoning Process
              <span className="ml-auto text-[10px] bg-slate-200 px-2 py-0.5 rounded-full group-open:hidden">View</span>
            </summary>
            <div className="px-4 pb-4 pt-2 border-t border-slate-100">
               <div className="space-y-3">
                 {reasoning.map((step, i) => (
                   <div key={i} className="flex gap-3 text-xs text-slate-600 font-mono">
                     <span className="text-emerald-500 font-bold">{i+1}.</span>
                     <span>{step}</span>
                   </div>
                 ))}
               </div>
            </div>
          </details>
        </div>
      )}
    </div>
  </motion.div>
);

const Assistant = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async (text = input) => {
    if (!text.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInput('');
    setIsTyping(true);

    try {
      // Mocking reasoning for now as simple endpoints might not return it yet, 
      // or if backend supports it, use it. 
      // Assuming backend returns { response: "...", reasoning: "..." }
      const response = await axios.post('http://localhost:8000/assistant/chat', { message: text });
      
      const aiResponse = response.data;

      // console.log(aiResponse)
      
      setMessages(prev => [...prev, { 
        role: 'ai', 
        reasoning: aiResponse.reasoning ? aiResponse.reasoning.split('\n') : ['Processing query...', 'Searching available records...', 'Formulating response'],
        content: aiResponse?.message || "I'm sorry, I couldn't process that request."
      }]);
    } catch (error) {
      console.error("Assistant failed:", error);
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: "I'm having trouble connecting to the server. Please try again."
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-2rem)] -mt-8 -mx-8 overflow-hidden bg-white">
      {/* History Sidebar */}
      <div className="hidden xl:flex w-72 border-r border-slate-100 flex-col bg-slate-50/50">
        <div className="p-4">
          <button onClick={() => setMessages([])} className="w-full flex items-center justify-center gap-2 bg-white border border-slate-200 hover:border-emerald-500 text-slate-600 hover:text-emerald-600 py-3 rounded-xl transition-all shadow-sm font-semibold">
            <Plus className="w-4 h-4" /> New Chat
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto px-4 space-y-4">
          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 px-2">Today</h4>
            <div className="space-y-1">
              {['Poaching Trends 2024', 'Ivory Seizure Report', 'Tiger Population Data'].map((title, i) => (
                <button key={i} className="w-full text-left px-3 py-2 rounded-lg text-sm text-slate-600 hover:bg-white hover:shadow-sm transition-all truncate flex items-center gap-2">
                  <MessageSquare className="w-3 h-3 text-slate-400 shrink-0" />
                  {title}
                </button>
              ))}
            </div>
          </div>
        </div>
        
        <div className="p-4 border-t border-slate-100">
           <div className="flex items-center gap-3 p-2 rounded-xl hover:bg-white transition-colors cursor-pointer">
             <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold text-xs">JD</div>
             <div className="flex-1 overflow-hidden">
               <p className="text-sm font-bold text-slate-900 truncate">John Doe</p>
               <p className="text-xs text-slate-500 truncate">Senior Analyst</p>
             </div>
             <MoreHorizontal className="w-4 h-4 text-slate-400" />
           </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative bg-white">
         {/* Decorative Background */}
         <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-emerald-50/50 via-transparent to-transparent pointer-events-none" />

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 relative z-10" ref={scrollRef}>
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center max-w-2xl mx-auto text-center space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
               <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-xl shadow-emerald-200">
                 <Bot className="w-8 h-8 text-white" />
               </div>
               <div>
                 <h1 className="text-3xl font-bold text-slate-900 mb-2">EcoGuard Intelligence</h1>
                 <p className="text-slate-500 max-w-md mx-auto">Your AI copilot for wildlife crime analysis. Ask me to dig through archives, summarize reports, or visualize trends.</p>
               </div>
               
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                 {SUGGESTED_QUERIES.map((q, i) => (
                   <button 
                     key={i} 
                     onClick={() => handleSend(q)}
                     className="text-left p-4 rounded-xl border border-slate-200 hover:border-emerald-300 hover:bg-emerald-50/30 transition-all text-sm text-slate-600 hover:text-emerald-700 font-medium group"
                   >
                     {q}
                     <span className="block mt-2 text-xs text-slate-400 group-hover:text-emerald-500">Generate Report &rarr;</span>
                   </button>
                 ))}
               </div>
            </div>
          ) : (
            messages.map((m, i) => <Message key={i} {...m} />)
          )}
          
          {isTyping && (
             <div className="flex gap-4 mb-8 items-center animate-in fade-in">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-sm bg-gradient-to-br from-emerald-500 to-emerald-600">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div className="bg-slate-50 border border-slate-100 px-4 py-3 rounded-2xl rounded-tl-sm flex items-center gap-1">
                   <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" />
                   <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                   <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                </div>
             </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 md:p-6 bg-white border-t border-slate-50 relative z-20">
          <div className="max-w-4xl mx-auto relative group">
             <div className="absolute inset-0 bg-emerald-500/5 rounded-2xl blur-xl group-hover:bg-emerald-500/10 transition-all" />
             <div className="relative bg-white border border-slate-200 focus-within:border-emerald-400 focus-within:ring-4 focus-within:ring-emerald-500/10 rounded-2xl shadow-sm transition-all flex items-end p-2 gap-2">
                <button className="p-2.5 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-xl transition-colors shrink-0">
                  <Paperclip className="w-5 h-5" />
                </button>
                <textarea 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if(e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder="Ask a question about incidents..."
                  className="flex-1 max-h-32 min-h-[44px] py-2.5 bg-transparent border-none focus:ring-0 text-slate-800 placeholder:text-slate-400 resize-none"
                  rows={1}
                />
                <div className="flex items-center gap-1">
                   <button className="p-2.5 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-xl transition-colors lg:hidden">
                      <Mic className="w-5 h-5" />
                   </button>
                   <button 
                      onClick={() => handleSend()}
                      disabled={!input.trim()}
                      className="p-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl shadow-lg shadow-emerald-500/20 disabled:opacity-50 disabled:shadow-none transition-all"
                   >
                      <Send className="w-5 h-5" />
                   </button>
                </div>
             </div>
             <p className="text-center text-[10px] text-slate-400 mt-2 font-medium">
               EcoGuard AI v2.0 • Data verified against official records
             </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Assistant;
