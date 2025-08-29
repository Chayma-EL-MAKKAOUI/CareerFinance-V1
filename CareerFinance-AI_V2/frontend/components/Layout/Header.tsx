import Link from 'next/link'

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="text-2xl font-bold text-blue-600">
            CareerPlatform
          </Link>
          
          <div className="flex items-center space-x-4">
            <button className="p-2 rounded-full hover:bg-gray-100 text-gray-600">
              👤
            </button>
            <button className="p-2 rounded-full hover:bg-gray-100 text-gray-600">
              ⚙️
            </button>
            <button className="p-2 rounded-full hover:bg-gray-100 text-gray-600">
              🚪
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}