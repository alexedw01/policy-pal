import { render, screen, fireEvent } from "@testing-library/react";
import SignUp from "../SignUp";

describe("SignUp Component", () => {
  test("renders sign-up form", () => {
    render(<SignUp />);
    expect(screen.getByText("Sign Up")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Username (no spaces)")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Password")).toBeInTheDocument();
  });

  test("disables sign-up button when fields are empty", () => {
    render(<SignUp />);
    const signUpButton = screen.getByText("Sign Up");
    expect(signUpButton).toBeDisabled();
  });

  test("shows error message if username contains spaces", () => {
    render(<SignUp />);
    const usernameInput = screen.getByPlaceholderText("Username (no spaces)");

    fireEvent.change(usernameInput, { target: { value: "invalid username" } });
    expect(screen.getByText("Username cannot contain spaces")).toBeInTheDocument();
  });

  test("enables sign-up button when inputs are valid", () => {
    render(<SignUp />);
    const usernameInput = screen.getByPlaceholderText("Username (no spaces)");
    const emailInput = screen.getByPlaceholderText("Email");
    const passwordInput = screen.getByPlaceholderText("Password");
    const signUpButton = screen.getByText("Sign Up");

    fireEvent.change(usernameInput, { target: { value: "validUsername" } });
    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "securePass123" } });

    expect(signUpButton).not.toBeDisabled();
  });

  test("alerts user when sign-up form is submitted correctly", () => {
    window.alert = jest.fn(); // Mock alert
    render(<SignUp />);
    
    fireEvent.change(screen.getByPlaceholderText("Username (no spaces)"), { target: { value: "validUsername" } });
    fireEvent.change(screen.getByPlaceholderText("Email"), { target: { value: "test@example.com" } });
    fireEvent.change(screen.getByPlaceholderText("Password"), { target: { value: "securePass123" } });
    
    fireEvent.click(screen.getByText("Sign Up"));
    
    expect(window.alert).toHaveBeenCalledWith("Sign-up form filled out correctly!");
  });
});
