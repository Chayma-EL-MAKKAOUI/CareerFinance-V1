import { ReactNode } from 'react'
import { cn } from '../../lib/utils'

interface CardProps {
  className?: string
  children: ReactNode
}

interface CardHeaderProps {
  className?: string
  children: ReactNode
}

interface CardTitleProps {
  className?: string
  children: ReactNode
}

interface CardContentProps {
  className?: string
  children: ReactNode
}

export function Card({ className, children }: CardProps) {
  return (
    <div className={cn("rounded-lg border bg-white shadow-sm", className)}>
      {children}
    </div>
  )
}

export function CardHeader({ className, children }: CardHeaderProps) {
  return (
    <div className={cn("flex flex-col space-y-1.5 p-6", className)}>
      {children}
    </div>
  )
}

export function CardTitle({ className, children }: CardTitleProps) {
  return (
    <h3 className={cn("text-2xl font-semibold leading-none tracking-tight", className)}>
      {children}
    </h3>
  )
}

export function CardContent({ className, children }: CardContentProps) {
  return (
    <div className={cn("p-6 pt-0", className)}>
      {children}
    </div>
  )
}