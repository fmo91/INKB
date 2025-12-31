import { render, screen } from '@testing-library/react-native';

import App from '../App';

describe('App', () => {
  it('renders the main heading', () => {
    render(<App />);
    expect(screen.getByText('INKB Reading Copilot')).toBeTruthy();
  });
});
