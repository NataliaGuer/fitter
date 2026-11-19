import { Card } from '@heroui/react'
import type { ComponentType, SVGProps } from 'react'

import { IconCircle } from '../IconCircle'

/** Home card whose content is not available yet: flat (border only, no shadow). */
export function PlaceholderCard({
  title,
  Icon,
  iconBgClassName,
}: {
  title: string
  Icon: ComponentType<SVGProps<SVGSVGElement>>
  iconBgClassName: string
}) {
  return (
    <Card className="shadow-none">
      <Card.Header className="flex-row items-center gap-3">
        <IconCircle Icon={Icon} bgClassName={iconBgClassName} />
        <div className="flex flex-col">
          <Card.Title className="text-lg font-bold">{title}</Card.Title>
          <Card.Description className="text-muted">in arrivo</Card.Description>
        </div>
      </Card.Header>
    </Card>
  )
}
