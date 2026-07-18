export interface ProblemDetail {
  type: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  items: T[];
  nextCursor: string | null;
  totalCount?: number;
}

export interface CursorPaginationParams {
  cursor?: string;
  limit?: number;
}

export function buildCursorParams(
  params: CursorPaginationParams & Record<string, unknown>
): Record<string, unknown> {
  const { cursor, limit = 25, ...rest } = params;
  return {
    ...rest,
    ...(cursor ? { cursor } : {}),
    limit,
  };
}

export function createAbortSignal(
  existingSignal?: AbortSignal
): { signal: AbortSignal; abort: () => void } {
  const controller = new AbortController();
  if (existingSignal) {
    existingSignal.addEventListener('abort', () => controller.abort());
  }
  return { signal: controller.signal, abort: () => controller.abort() };
}

export function parseProblemDetail(error: unknown): ProblemDetail | null {
  if (typeof error !== 'object' || error === null) return null;
  const candidate = error as Partial<ProblemDetail>;
  if (typeof candidate.status === 'number' && typeof candidate.title === 'string') {
    return {
      type: candidate.type || 'about:blank',
      title: candidate.title,
      status: candidate.status,
      detail: candidate.detail,
      instance: candidate.instance,
      errors: candidate.errors,
    };
  }
  return null;
}
