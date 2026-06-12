import { Controller, Get, Logger } from "@nestjs/common";
import {
  HealthCheck,
  HealthCheckResult,
  HealthCheckService,
  MemoryHealthIndicator,
  TypeOrmHealthIndicator,
} from "@nestjs/terminus";
import { Public } from "@common/decorators/public.decorator";
import { ApiTags } from "@nestjs/swagger";

@ApiTags("Health")
@Controller("health")
export class HealthController {
  private readonly logger = new Logger(HealthController.name);

  constructor(
    private readonly health: HealthCheckService,
    private readonly db: TypeOrmHealthIndicator,
    private readonly memory: MemoryHealthIndicator,
  ) {}

  @Public()
  @Get()
  @HealthCheck()
  async check(): Promise<HealthCheckResult> {
    this.logger.debug("GET /health — running health checks");
    const result = await this.health.check([
      () => this.db.pingCheck("database"),
      () => this.memory.checkHeap("memory_heap", 300 * 1024 * 1024),
    ]);
    const status = result.status;
    if (status === "ok") {
      this.logger.debug("Health check passed");
    } else {
      this.logger.warn(`Health check degraded — status: ${status}`);
    }
    return result;
  }
}
