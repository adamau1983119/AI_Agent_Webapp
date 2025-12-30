import { Link } from 'react-router-dom'
import type { Topic } from '@/types'

interface TopicCardProps {
  topic: Topic
}

const gradientClasses = {
  fashion: 'from-purple-400 to-blue-400',
  food: 'from-orange-400 to-pink-400',
  trend: 'from-green-400 to-blue-400',
}

export default function TopicCard({ topic }: TopicCardProps) {
  // 從 topic 數據計算進度
  const contentProgress = topic.wordCount > 0 ? Math.min(100, (topic.wordCount / 500) * 100) : 0
  const imageProgress = topic.imageCount >= 8 ? 100 : Math.min(100, (topic.imageCount / 8) * 100)

  return (
    <Link to={`/topics/${topic.id}`}>
      <div className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow">
        <div className={`h-32 bg-gradient-to-br ${gradientClasses[topic.category]}`}></div>
        <div className="p-4">
          <h3 className="font-bold text-lg mb-3">{topic.title}</h3>
          <div className="space-y-2 mb-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">內容完成度</span>
                <span className="font-semibold">{contentProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: `${contentProgress}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">圖片完成度</span>
                <span className="font-semibold">{imageProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-secondary h-2 rounded-full"
                  style={{ width: `${imageProgress}%` }}
                ></div>
              </div>
            </div>
          </div>
          <button className="text-primary hover:text-primary-dark font-medium text-sm">
            View more →
          </button>
        </div>
      </div>
    </Link>
  )
}

