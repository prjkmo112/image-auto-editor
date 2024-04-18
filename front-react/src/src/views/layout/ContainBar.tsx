/**
 * 좌측, 상단 바가 모두 포함된 레이아웃입니다
 */
import React, { Component } from "react";
import { IconButton, Drawer, Box, List, ListItem, ListItemButton, ListItemText, Divider } from "@mui/material";
import { Outlet } from 'react-router-dom';
import { Menu } from '@mui/icons-material';

import { StateTypes } from 'types';
import api from 'api';
import Utils from 'comp/Utils';
import styles from './containbar.module.scss';



class ContainBar extends Component<StateTypes.ContainerBarProps<"rrd">, StateTypes.ContainerBarState> {
  constructor(props:StateTypes.ContainerBarProps<"rrd">) {
    super(props);
    this.state = {
      openLeftbar: false
    }
  }

  toggleDrawer = (newOpen:boolean) => {
    this.setState({ openLeftbar: newOpen });
  }

  changeMenu = (menu:{key:string}) => {
    this.setState({ openLeftbar: false }, () => {
      if (menu.key === "home")
        this.props.navigate("/", { replace: false });
      else
        this.props.navigate(`/${menu.key}`, { replace: false })
    });
  }
  
  render(): React.ReactNode {
    return (
      <>
        <div className={styles.header}>
          <IconButton onClick={(e) => this.toggleDrawer(true)}>
            <Menu />
          </IconButton>
        </div>

        <Divider />

        <div className={styles.body}>
          {/* title */}
          <div className={`${styles.title_cont} ${styles[`lang${process.env.LANGUAGE}`]}`}>
            <h3>{Utils.inform.getUrlInfo(this.props.location)['title'][process.env.LANGUAGE as "en"|"ko"]}</h3>
          </div>

          <Outlet />
        </div>

        <div>
          <Drawer open={this.state.openLeftbar} onClose={(e, key) => this.toggleDrawer(false)}>
            <Box sx={{ width: 250 }}>
              <List>
                <ListItem key="home">
                  <ListItemButton onClick={(e) => this.changeMenu({key: "home"})}>
                    <ListItemText secondary={ process.env.LANGUAGE === "ko" ? "홈" : "HOME" } />
                  </ListItemButton>
                </ListItem>
                {api.menu.menu_list.map((menu) => {
                  let text = menu.enname;
                  if (process.env.LANGUAGE === "ko")
                    text = menu.krname;

                  return (
                    <ListItem key={menu.key}>
                      <ListItemButton onClick={() => this.changeMenu(menu)}>
                        <ListItemText secondary={text} />
                      </ListItemButton>
                    </ListItem>
                  )
                })}
              </List>
            </Box>
          </Drawer>
        </div>
      </>
    )
  }
}

export default ContainBar;