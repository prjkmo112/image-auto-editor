import React, { Component } from "react";
import { Input, Box, Grid, Skeleton, IconButton, Tooltip } from "@mui/material";
import { Lightbulb } from '@mui/icons-material';
import { StateTypes } from 'types';

import API from 'api';
import styles from './exceptimg.module.scss';


function getText(type:string) {
  if (type === "input_placeholder") {
    if (process.env.LANGUAGE === "en")
      return "code filter"
    else if (process.env.LANGUAGE === "ko")
      return "코드 검색"
  } else if (type === "tooltip_bulb") {
    if (process.env.LANGUAGE)
      return "Switch screen to black and white (useful for measuring image size)"
    else if (process.env.LANGUAGE === "ko")
      return "화면 흑백전환 (이미지 크기 가늠할 때 유용함)"
  }
}


class ExceptImg extends Component<StateTypes.ExceptImgProps, StateTypes.ExceptImgState> {
  constructor(props:StateTypes.ExceptImgProps) {
    super(props);
    this.state = {
      img_search_code: "",
      content_loading: false,
      img_list: []
    }
  }

  onInput = (e:React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    e.preventDefault();
    
    if (/^[A-Za-z]*$/.test(e.target.value)) {
      this.setState({ content_loading: true, img_search_code: e.target.value }, () => {
        if (e.target.value !== "") {
          API.getimg.excepted(e.target.value, true, (err, res) => {
            this.setState({ content_loading: false, img_list: res });
          })
        } else {
          this.setState({ content_loading: false });
        }
      });
    }
  }

  turnTheme = (e:React.MouseEvent) => {
    e.preventDefault();

    if (document.body.hasAttribute('data-theme'))
      document.body.removeAttribute('data-theme');
    else
      document.body.setAttribute('data-theme', "dark");
  }

  render(): React.ReactNode {
    return (
      <>
        <Input 
          multiline={false} 
          placeholder={getText("input_placeholder")} 
          value={this.state.img_search_code} 
          onChange={(e) => this.onInput(e)} 
          className={styles['MuiInput-input']}
        />
        
        <Tooltip title={getText("tooltip_bulb")} style={{ marginLeft: "30px" }}>
          <IconButton onClick={(e) => this.turnTheme(e)}>
            <Lightbulb className={styles['lightbulb-icon']} />
          </IconButton>
        </Tooltip>

        <div className={styles.content}>
          {!!this.state.img_search_code && (
            <Grid container spacing={3}>
              {(this.state.content_loading ? Array.from(new Array(6)) : this.state.img_list).map((item) => {
                return (
                  <Grid item xs={4}>
                    <Box className={`${styles['MuiBox-root']} ${styles.galleryitem}`}>
                      {this.state.content_loading ? (
                        <Skeleton variant="rectangular" className={styles['MuiSkeleton-root']} />
                      ) : (
                        <>
                          <img src={`data:image/png;base64,${item.image}`} className={styles['gallery-item']} loading="lazy" />
                          <div className={styles.img_code_box}>
                            <span>{item.code}</span>
                          </div>
                        </>
                      )}
                    </Box>
                  </Grid>
                )
              })}
            </Grid>
          )}
        </div>
      </>
    )
  }
}

export default ExceptImg