# Alert và Runbook

Mỗi alert dựa trên triệu chứng hướng tới người dùng hoặc SLO, không dựa trực tiếp vào tên của thành phần implementation nội bộ.

## Alert 1

- Tên: `high_latency_p95`
- Severity: `warning`
- SLI/SLO liên quan: `latency_p95_ms`; mục tiêu là P95 latency dưới 3000 ms với target 99.5%.
- Điều kiện kích hoạt: `latency_p95 > 3000ms for 5 minutes`.
- Ảnh hưởng tới người dùng: Các request chậm hơn ba giây ở mức P95; người dùng có thể gặp phản hồi chậm, timeout hoặc bỏ dở thao tác.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận alert đang active và so sánh latency P50/P95/P99 với lưu lượng request và baseline gần nhất.
  2. Kiểm tra error rate, timeout rate, endpoint hoặc region bị ảnh hưởng để xác định triệu chứng xảy ra trên diện rộng hay chỉ cục bộ.
  3. Xem các lần deploy, thay đổi cấu hình gần đây, latency của dependency và tình trạng quá tải tài nguyên (CPU, memory, queue depth).
- Mitigation tạm thời: Giảm các tác vụ không bắt buộc hoặc kích thước response, chuyển traffic sang capacity pool khỏe mạnh và rollback thay đổi gần nhất nếu có tương quan với sự cố.
- Owner: `on-call-engineer`

## Alert 2

- Tên: `elevated_error_rate`
- Severity: `critical`
- SLI/SLO liên quan: `error_rate_pct`; mục tiêu là error rate dưới 2% với target 99.0%.
- Điều kiện kích hoạt: `error_rate_pct > 5 for 3 minutes`.
- Ảnh hưởng tới người dùng: Hơn một trên hai mươi request có thể thất bại, gây ra thông báo lỗi, response bị thiếu hoặc thao tác của người dùng không hoàn tất.
- Ba bước kiểm tra đầu tiên:
  1. Xác minh cách tính error rate và xác định nhóm status/error chiếm đa số, endpoint, region và phân khúc traffic bị ảnh hưởng.
  2. Kiểm tra tình trạng dependency, lỗi authentication/configuration, rate limit và tình trạng quá tải tài nguyên.
  3. Đối chiếu thời điểm bắt đầu với release, feature flag, thay đổi dữ liệu/cấu hình gần nhất hoặc sự cố của dịch vụ bên ngoài.
- Mitigation tạm thời: Dừng hoặc rollback thay đổi đáng ngờ, tắt feature không bắt buộc bị ảnh hưởng, chuyển traffic sang capacity pool khỏe mạnh và thông báo phần chức năng đang bị suy giảm.
- Owner: `on-call-engineer`

## Alert 3

- Tên: `cost_budget_exceeded`
- Severity: `warning`
- SLI/SLO liên quan: `daily_cost_usd`; mục tiêu là chi phí mỗi ngày không vượt quá $2.50 với target 100%.
- Điều kiện kích hoạt: `daily_cost_usd > 2.5`.
- Ảnh hưởng tới người dùng: Dịch vụ có thể phải throttle hoặc giảm chức năng để giữ ngân sách, làm tăng thời gian chờ hoặc giới hạn các tính năng không bắt buộc.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận tổng chi phí trong ngày, time window, currency và kiểm tra dữ liệu usage bị trùng hoặc cập nhật trễ có làm số liệu tăng giả hay không.
  2. Phân rã chi phí theo request volume, model/provider, token usage, retry và nhóm request tốn kém; so sánh với baseline hằng ngày.
  3. Kiểm tra traffic spike, retry loop, prompt/response tăng kích thước, batch job và các thay đổi gần đây về pricing hoặc configuration.
- Mitigation tạm thời: Áp dụng rate limit hoặc quota cho request, giảm retry và output không cần thiết, chuyển traffic phù hợp sang lựa chọn có chi phí thấp hơn và tạm dừng job không thiết yếu.
- Owner: `team-lead`
