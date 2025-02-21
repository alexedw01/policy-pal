import { render, screen, fireEvent } from "@testing-library/react";
import Login from "../Login";

describe("Login Component", () => {
  test("renders login form", () => {
    render(<Login />);
    expect(screen.getByText("Login")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Username (no spaces)")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Password")).toBeInTheDocument();
  });

  test("disables login button when fields are empty", () => {
    render(<Login />);
    const loginButton = screen.getByText("Login");
    expect(loginButton).toBeDisabled();
  });

  test("shows error message if username contains spaces", () => {
    render(<Login />);
    const usernameInput = screen.getByPlaceholderText("Username (no spaces)");

    fireEvent.change(usernameInput, { target: { value: "invalid username" } });
    expect(screen.getByText("Username cannot contain spaces")).toBeInTheDocument();
  });

  test("enables login button when inputs are valid", () => {
    render(<Login />);
    const usernameInput = screen.getByPlaceholderText("Username (no spaces)");
    const passwordInput = screen.getByPlaceholderText("Password");
    const loginButton = screen.getByText("Login");

    fireEvent.change(usernameInput, { target: { value: "validUsername" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });

    expect(loginButton).not.toBeDisabled();
  });

  test("alerts user when login form is submitted correctly", () => {
    window.alert = jest.fn(); // Mock alert
    render(<Login />);
    
    fireEvent.change(screen.getByPlaceholderText("Username (no spaces)"), { target: { value: "validUsername" } });
    fireEvent.change(screen.getByPlaceholderText("Password"), { target: { value: "password123" } });
    
    fireEvent.click(screen.getByText("Login"));
    
    expect(window.alert).toHaveBeenCalledWith("Login form filled out correctly!");
  });
});
