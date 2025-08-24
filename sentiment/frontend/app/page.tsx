import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardStats } from "@/components/dashboard-stats"
import { SentimentLineChart } from "@/components/sentiment-line-chart"
import { SentimentBarChart } from "@/components/sentiment-bar-chart"
import { PostsDataTable } from "@/components/posts-data-table"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />
      <main className="container mx-auto px-4 py-6 space-y-6">
        <DashboardStats />

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-card rounded-lg border shadow-sm transition-all hover:shadow-md">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Sentiment Over Time</h2>
                <div className="text-sm text-muted-foreground">Rolling 2-hour average</div>
              </div>
              <SentimentLineChart />
            </div>
          </div>
          <div className="bg-card rounded-lg border shadow-sm transition-all hover:shadow-md">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Sentiment Distribution</h2>
                <div className="text-sm text-muted-foreground">Last 24 hours</div>
              </div>
              <SentimentBarChart />
            </div>
          </div>
        </div>

        {/* Table Section */}
        <div className="bg-card rounded-lg border shadow-sm transition-all hover:shadow-md">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold">Recent Posts</h2>
              <div className="text-sm text-muted-foreground">Real-time social media mentions</div>
            </div>
            <PostsDataTable />
          </div>
        </div>
      </main>
    </div>
  )
}
