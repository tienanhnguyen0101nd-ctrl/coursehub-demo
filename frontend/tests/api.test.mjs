// Kiem thu ham api() voi fetch gia lap. Khong goi Backend/PostgreSQL that.
import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { api } from "../src/api.js";

const originalFetch = globalThis.fetch;
afterEach(() => {
  globalThis.fetch = originalFetch;
});

function mockResponse(status, raw = "") {
  return {
    ok: status >= 200 && status < 300,
    status,
    text: async () => raw,
  };
}

test("1. GET 200 tra ve JSON va goi dung URL mac dinh", async () => {
  let calledUrl;
  let calledOptions;
  globalThis.fetch = async (url, options) => {
    calledUrl = url;
    calledOptions = options;
    return mockResponse(200, JSON.stringify([{ class_id: "WEB-01" }]));
  };
  const data = await api("/sections");
  assert.equal(calledUrl, "http://127.0.0.1:8000/sections");
  assert.equal(calledOptions.method, "GET");
  assert.deepEqual(calledOptions.headers, {});
  assert.equal(calledOptions.body, undefined);
  assert.deepEqual(data, [{ class_id: "WEB-01" }]);
});

test("2. POST 201 gui JSON body va Content-Type", async () => {
  let calledOptions;
  globalThis.fetch = async (_url, options) => {
    calledOptions = options;
    return mockResponse(201, JSON.stringify({ message: "Dang ky thanh cong" }));
  };
  const body = { student_id: "22000004", class_section_id: "WEB-01" };
  const data = await api("/enrollments", { method: "POST", body });
  assert.equal(calledOptions.method, "POST");
  assert.equal(calledOptions.headers["Content-Type"], "application/json");
  assert.equal(calledOptions.body, JSON.stringify(body));
  assert.equal(data.message, "Dang ky thanh cong");
});

test("3. DELETE 204 tra null, khong doc JSON", async () => {
  globalThis.fetch = async () => ({
    ok: true,
    status: 204,
    text: async () => {
      throw new Error("Khong duoc doc body cua 204");
    },
  });
  const data = await api("/enrollments/22000004/WEB-01", { method: "DELETE" });
  assert.equal(data, null);
});

test("4. 404 nem loi kem status va detail", async () => {
  globalThis.fetch = async () =>
    mockResponse(404, JSON.stringify({ detail: "Khong tim thay sinh vien" }));
  await assert.rejects(api("/students/99999999/enrollments"), (error) => {
    assert.equal(error.status, 404);
    assert.equal(error.message, "HTTP 404: Khong tim thay sinh vien");
    return true;
  });
});

test("5. 409 nem loi xung dot", async () => {
  globalThis.fetch = async () =>
    mockResponse(409, JSON.stringify({ detail: "Lop hoc phan da het cho" }));
  await assert.rejects(
    api("/enrollments", { method: "POST", body: {} }),
    (error) => {
      assert.equal(error.status, 409);
      assert.match(error.message, /het cho/);
      return true;
    },
  );
});

test("6. 422 ghep danh sach detail thanh chuoi", async () => {
  globalThis.fetch = async () =>
    mockResponse(
      422,
      JSON.stringify({ detail: [{ msg: "Field required" }, { msg: "String too short" }] }),
    );
  await assert.rejects(
    api("/enrollments", { method: "POST", body: {} }),
    (error) => {
      assert.equal(error.status, 422);
      assert.equal(error.message, "HTTP 422: Field required; String too short");
      return true;
    },
  );
});

test("7. Phan hoi khong phai JSON bao loi ro rang", async () => {
  globalThis.fetch = async () => mockResponse(500, "<html>Internal Server Error</html>");
  await assert.rejects(api("/sections"), /HTTP 500: phản hồi không phải JSON/);
});

test("8. Loi mang bao kiem tra Backend/CORS; AbortError giu nguyen", async () => {
  globalThis.fetch = async () => {
    throw new TypeError("Failed to fetch");
  };
  await assert.rejects(api("/sections"), /Kiểm tra Backend\/CORS/);

  globalThis.fetch = async () => {
    const error = new Error("aborted");
    error.name = "AbortError";
    throw error;
  };
  await assert.rejects(api("/sections"), (error) => error.name === "AbortError");
});

