import styled from 'styled-components'
import PPLogo from '../images/policypal.svg'
import UserSVG from '../images/usericon.svg'
import HamSVG from '../images/hamburgericon.svg'

const HeaderContainer = styled("div")`
	z-index: 1;

	position: -webkit-sticky;
	position: sticky;

  	top: 0;
  	width: 100%;
 	padding: 1em 0;

  	background: #0F1FAD;
  	color: white;

  	display: flex;
  	justify-content: space-between;
  	align-items: center;

	font-family: 'ITC Century';
	font-style: normal;
	font-weight: 400;
	text-align: center;
	text-transform: uppercase;
	font-size: 18px;
	line-height: 21.6px;
`;

const Left = styled("div")`
	display: flex;
	align-items: center;
	justify-content: flex-start;
	padding-left: 20px;
`;

const Center = styled("div")`
	display: flex;
	align-items: center;
	justify-content: center;
	flex-grow: 1;
`;

const Right = styled("div")`
	display: flex;
	align-items: center;
	justify-content: flex-end;
	padding-right: 20px;
`;

const Logo = styled("img")`
	height: 30px;
	cursor: pointer;
`;

const logoheight = 60;

const HamburgerIcon = styled("img")`
	height: ${logoheight}px;
	cursor: pointer;
`;

const UserIcon = styled("img")`
	height: ${logoheight}px;
	cursor: pointer;
`;

const Header = () => {
	return (
		<HeaderContainer>
		{/* Daily Bruin */}
			<Left>
				<a href="https://google.com">
					<HamburgerIcon
						src={HamSVG}
						alt="Menu"
					/>
				</a>
			</Left>
			<Center>
				<a href="https://google.com">
					<Logo
						src={PPLogo}
						alt="Policy Pal"
					/>
				</a>
			</Center>
			<Right>
				<a href="https://google.com">
					<UserIcon
						src={UserSVG}
						alt="User Login"
					/>
				</a>
			</Right>
		</HeaderContainer>
	)
}

export default Header;