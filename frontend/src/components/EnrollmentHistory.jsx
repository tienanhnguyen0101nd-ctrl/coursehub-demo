import { useEffect, useState } from "react";
import { api } from "../api.js";

const PAGE_SIZE = 5;

export default function EnrollmentHistory({ studentId, refresh }) {
  const [events, setEvents] = useState([]);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setPage(0);
  }, [studentId]);

  useEffect(() => {
    const controller = new AbortController();
    const skip = page * PAGE_SIZE;
    const limit = PAGE_SIZE + 1;
    const query = new URLSearchParams({
      dataset: "demo",
      student_id: studentId,
      skip: String(skip),
      limit: String(limit),
    });

    async function loadEvents() {
      setLoading(true);
      setError("");
      try {
        const data = await api(`/enrollment-events?${query.toString()}`, {
          signal: controller.signal,
        });
        if (controller.signal.aborted) return;
        setHasMore(data.length > PAGE_SIZE);
        setEvents(data.slice(0, PAGE_SIZE));
      } catch (err) {
        if (controller.signal.aborted) return;
        setError(err.message);
        setEvents([]);
        setHasMore(false);
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }

    loadEvents();
    return () => controller.abort();
  }, [studentId, page, refresh]);

  return (
    <section className="panel">
      <h2>4. Lịch sử đăng ký (nhật ký demo)</h2>
      <p className="muted">
        Sinh viên <strong>{studentId}</strong> · Trang {page + 1} (tối đa {PAGE_SIZE} sự kiện/trang, chỉ đọc <code>dataset = demo</code>)
      </p>
      {error && <p className="notice error">{error}</p>}
      {loading ? (
        <p className="muted">Đang tải lịch sử...</p>
      ) : events.length === 0 ? (
        <p>Chưa có sự kiện demo nào cho sinh viên này.</p>
      ) : (
        <div className="table-scroll">
          <table aria-label="Lịch sử sự kiện đăng ký">
            <thead>
              <tr>
                <th>ID</th>
                <th>Lớp</th>
                <th>Loại sự kiện</th>
                <th>Nguồn</th>
                <th>Thời điểm</th>
              </tr>
            </thead>
            <tbody>
              {events.map((ev) => (
                <tr key={ev.id}>
                  <td>{ev.id}</td>
                  <td><strong>{ev.class_section_id}</strong></td>
                  <td>
                    <span className={ev.event_type === "CREATED" ? "badge" : "badge full"}>
                      {ev.event_type}
                    </span>
                  </td>
                  <td>{ev.source}</td>
                  <td>{String(ev.occurred_at).replace("T", " ").slice(0, 19)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="pagination">
        <button
          type="button"
          className="secondary"
          disabled={loading || page === 0}
          onClick={() => setPage((p) => Math.max(0, p - 1))}
        >
          ← Trang trước
        </button>
        <button
          type="button"
          className="secondary"
          disabled={loading || !hasMore}
          onClick={() => setPage((p) => p + 1)}
        >
          Trang sau →
        </button>
      </div>
    </section>
  );
}
