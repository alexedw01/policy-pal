'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';

const API_BASE = "http://127.0.0.1:8080/api";

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [age, setAge] = useState(''); 
  const [gender, setGender] = useState('');
  const [ethnicity, setEthnicity] = useState('');
  const [state, setPlace] = useState('');
  const [political_affiliation, setPoliticalAffiliation] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();
  const { setUser } = useUser();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
  
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(
          isLogin 
            ? { email, password }
            : { email, password, username, age, gender, ethnicity, state, political_affiliation }
        ),
      });
  
      const data = await response.json();
  
      if (!response.ok) {
        throw new Error(data.error || 'Authentication failed');
      }
  
      localStorage.setItem('token', data.access_token);
      if (data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
        setUser(data.user); 
      }
      
      router.push('/');
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    }
  };  

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
          {isLogin ? 'Sign in to your account' : 'Create a new account'}
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 rounded-md p-4">
              {error}
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            {!isLogin && (
              <>
                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                    Username
                  </label>
                  <div className="mt-1">
                    <input
                      id="username"
                      name="username"
                      type="text"
                      required
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="age" className="block text-sm font-medium text-gray-700">
                    Age
                  </label>
                  <div className="mt-1">
                    <input
                      id="age"
                      name="age"
                      type="number"
                      min="0"
                      required
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                      className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="gender" className="block text-sm font-medium text-gray-700">
                    Gender
                  </label>
                  <div className="mt-1">
                    <select
                      id="gender"
                      name="gender"
                      required
                      value={gender}
                      onChange={(e) => setGender(e.target.value)}
                      className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                    >
                      <option value="">Select your Gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="non-binary">Non-binary</option>
                      <option value="transgender">Transgender</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label htmlFor="ethnicity" className="block text-sm font-medium text-gray-700">
                    Ethnicity
                  </label>
                  <div className="mt-1">
                    <select
                      id="ethnicity"
                      name="ethnicity"
                      required
                      value={ethnicity}
                      onChange={(e) => setEthnicity(e.target.value)}
                      className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                    >
                      <option value="">Select your Ethnicity</option>
                      <option value="hispanic or latino">Hispanic or Latino</option>
                      <option value="white">White</option>
                      <option value="black or african american">Black or African American</option>
                      <option value="asian">Asian</option>
                      <option value="native hawaiian or other pacific islander">Native Hawaiian or Other Pacific Islander</option>
                      <option value="american indian or alaska native">American Indian or Alaska Native</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label htmlFor="state" className="block text-sm font-medium text-gray-700">
                    State
                  </label>
                  <div className="mt-1">
                    <select
                      id="state"
                      name="state"
                      required
                      value={state}
                      onChange={(e) => setPlace(e.target.value)}
                      className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                    >
                      <option value="">Select your State</option> 
                      <option value="alabama">Alabama</option> 
                      <option value="alaska">Alaska</option> 
                      <option value="arizona">Arizona</option> 
                      <option value="arkansas">Arkansas</option> 
                      <option value="california">California</option> 
                      <option value="colorado">Colorado</option> 
                      <option value="connecticut">Connecticut</option> 
                      <option value="delaware">Delaware</option> 
                      <option value="florida">Florida</option> 
                      <option value="georgia">Georgia</option> 
                      <option value="hawaii">Hawaii</option> 
                      <option value="idaho">Idaho</option> 
                      <option value="illinois">Illinois</option> 
                      <option value="indiana">Indiana</option> 
                      <option value="iowa">Iowa</option> 
                      <option value="kansas">Kansas</option> 
                      <option value="kentucky">Kentucky</option> 
                      <option value="louisiana">Louisiana</option> 
                      <option value="maine">Maine</option> 
                      <option value="maryland">Maryland</option> 
                      <option value="massachusetts">Massachusetts</option> 
                      <option value="michigan">Michigan</option> 
                      <option value="minnesota">Minnesota</option> 
                      <option value="mississippi">Mississippi</option> 
                      <option value="missouri">Missouri</option> 
                      <option value="montana">Montana</option> 
                      <option value="nebraska">Nebraska</option> 
                      <option value="nevada">Nevada</option> 
                      <option value="new hampshire">New Hampshire</option> 
                      <option value="new jersey">New Jersey</option> 
                      <option value="new mexico">New Mexico</option> 
                      <option value="new york">New York</option> 
                      <option value="north carolina">North Carolina</option> 
                      <option value="north dakota">North Dakota</option> 
                      <option value="ohio">Ohio</option> 
                      <option value="oklahoma">Oklahoma</option> 
                      <option value="oregon">Oregon</option> 
                      <option value="pennsylvania">Pennsylvania</option> 
                      <option value="rhode island">Rhode Island</option> 
                      <option value="south carolina">South Carolina</option> 
                      <option value="south dakota">South Dakota</option> 
                      <option value="tennessee">Tennessee</option> 
                      <option value="texas">Texas</option> 
                      <option value="utah">Utah</option> 
                      <option value="vermont">Vermont</option> 
                      <option value="virginia">Virginia</option> 
                      <option value="washington">Washington</option> 
                      <option value="west virginia">West Virginia</option> 
                      <option value="wisconsin">Wisconsin</option> 
                      <option value="wyoming">Wyoming</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label htmlFor="political_affiliation" className="block text-sm font-medium text-gray-700">
                    Political Affiliation
                  </label>
                  <div className="mt-1">
                    <select
                      id="political_affiliation"
                      name="political_affiliation"
                      required
                      value={political_affiliation}
                      onChange={(e) => setPoliticalAffiliation(e.target.value)}
                      className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                    >
                      <option value="">Select your Political Affiliation</option>
                      <option value="libertarian">Libertarian</option>
                      <option value="conservative">Conservative</option>
                      <option value="progressive">Progressive</option>
                      <option value="moderate">Moderate</option>
                      <option value="socialist">Socialist</option>
                      <option value="communist">Communist</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>

              </>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email Address
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {isLogin ? 'Sign in' : 'Register'}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="w-full text-center text-sm text-blue-600 hover:text-blue-500"
            >
              {isLogin ? 'Need an account? Sign up' : 'Already have an account? Sign in'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
